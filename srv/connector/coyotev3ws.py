import json, uuid, traceback, asyncio, time
from loguru import logger
import websockets
from websockets.legacy.protocol import WebSocketCommonProtocol

from srv import WS_CONNECTIONS, DEFAULT_WAVE #, WS_CONNECTIONS_ID_REVERSE, WS_BINDS

# Global state for keep-alive heartbeat
LAST_ACTIVITY_TIME = {'A': 0, 'B': 0}
KEEPALIVE_POWER = 1
KEEPALIVE_INTERVAL = 10
KEEPALIVE_WAVE = '["0101010101010101"]'

WAKEUP_POWER = 1
WAKEUP_WAVE = '["0101010101010101"]'

class DGWSMessage():
    HEARTBEAT = json.dumps({'type': 'heartbeat', 'clientId': '', 'targetId': '', 'message': '200'})
    def __init__(self, type, clientId="", targetId="", message="") -> None:
        self.type = type
        self.clientId = clientId
        self.targetId = targetId
        self.message = message
    
    def __str__(self) -> str:
        return json.dumps({
            'type': self.type,
            'clientId': self.clientId,
            'targetId': self.targetId,
            'message': str(self.message),
        })
    async def send(self, conn):
        msg = self.__str__()
        ret = await conn.ws_conn.send(msg)
        return ret

class DGConnection():
    def __init__(self, ws_connection: WebSocketCommonProtocol, client_uuid=None, SETTINGS:dict=None) -> None:
        if SETTINGS is None:
            raise ValueError("DGConnection SETTINGS not provided.")
        self.ws_conn = ws_connection
        if client_uuid is None:
            client_uuid = ws_connection.id
        self.uuid = str(client_uuid)

        self.SETTINGS = SETTINGS
        self.master_uuid = SETTINGS['ws']['master_uuid']

        limit_a = SETTINGS['dglab3']['channel_a']['strength_limit']
        limit_b = SETTINGS['dglab3']['channel_b']['strength_limit']

        self.strength       = {'A':0, 'B':0}
        self.strength_max   = {'A':0, 'B':0}
        self.strength_limit = {'A':limit_a, 'B':limit_b}

        WS_CONNECTIONS.add(self)
        # WS_CONNECTIONS_ID_REVERSE[self.uuid] = self
    
    def __str__(self):
        return f"<DGConnection (id:{self.uuid}, {self.strength}, max {self.strength_max})>"
    
    async def msg_handler(self, msg: DGWSMessage):
        if msg.type == 'bind':
            # APP send bind request
            # WS_BINDS[self] = WS_CONNECTIONS_ID_REVERSE[msg.targetId] 
            assert msg.targetId == self.uuid, "UUID mismatch."
            assert msg.clientId == self.master_uuid, "Binding to unknown uuid."
            ret = DGWSMessage('bind', clientId=msg.clientId, targetId=msg.targetId, message='200')
            await ret.send(self)
            logger.success(f'Device {self.uuid[:8]} bound successfully')
        elif msg.type == 'msg':
            if msg.message.startswith('strength-'):
                self.strength['A'], self.strength['B'], self.strength_max['A'], self.strength_max['B'] = map(int, msg.message[len('strength-'):].split('+'))
                for chann in ['A', 'B']:
                    limit = self.get_upper_strength(chann)
                    if (self.strength[chann] != 0 and self.strength[chann] != limit):
                        await self.set_strength(chann, value=limit)
            elif msg.message.startswith('feedback-'):
                pass
            else:
                logger.warning(f'Device {self.uuid[:8]} unknown message: {msg.message}')
        elif msg.type == 'heartbeat':
            pass
    
    def get_upper_strength(self, channel='A'):
        return min(self.strength_max[channel], self.strength_limit[channel])

    async def set_strength(self, channel='A', mode='2', value=0, force=False, allow_exceed=False):
        if not force:
            if value < 0 or value > 200:
                raise ValueError()
            limit = self.get_upper_strength(channel)
            if value > int(limit) and mode == '2':
                if allow_exceed:
                    # Boost exceeds limit - allow it but cap at hardware max
                    hw_max = self.strength_max.get(channel, 200)
                    value = min(value, hw_max)
                    logger.warning(f'Device {self.uuid[:8]} Channel {channel}: ⚡ BOOST {value} exceeds limit {limit}!')
                else:
                    logger.warning(f'Device {self.uuid[:8]} Channel {channel}: strength {value} exceeds limit {limit}, clamping')
                    value = limit
            # Update activity time only for real usage (not forced keep-alive)
            if value > KEEPALIVE_POWER:
                LAST_ACTIVITY_TIME[channel] = time.time()
        if mode == '2':
            self.strength[channel] = value
        msg = DGWSMessage('msg', self.master_uuid, self.uuid, f"strength-{'1' if channel == 'A' else '2'}+{mode}+{value}")
        await msg.send(self)

    async def set_strength_0_to_1(self, channel='A', value=0):
        if value < 0 or value > 1:
            raise ValueError()
        limit = self.get_upper_strength(channel)
        strength = int(limit * value)
        await self.set_strength(channel=channel, mode='2', value=strength)
    
    async def set_strength_with_limit(self, channel='A', value_0_to_1=0, device_limit=100, allow_exceed=False):
        """Set strength using a specific device limit (for dynamic power control)"""
        if value_0_to_1 < 0 or value_0_to_1 > 1:
            value_0_to_1 = max(0, min(1, value_0_to_1))
        # Use the minimum of device_limit and hardware max
        effective_limit = min(self.strength_max.get(channel, 200), device_limit)
        strength = int(effective_limit * value_0_to_1)
        await self.set_strength(channel=channel, mode='2', value=strength, allow_exceed=allow_exceed)

    async def send_wave(self, channel='A', wavestr=DEFAULT_WAVE):
        # Update activity time to prevent keep-alive during active usage
        LAST_ACTIVITY_TIME[channel] = time.time()
        msg = DGWSMessage('msg', self.master_uuid, self.uuid, f"pulse-{channel}:{wavestr}")
        await msg.send(self)
    
    async def clear_wave(self, channel='A'):
        channel = '1' if channel == 'A' else '2'
        msg = DGWSMessage('msg', self.master_uuid, self.uuid, f"clear-{channel}")
        await msg.send(self)
    
    async def send_err(self, type=''):
        msg = DGWSMessage(type, )
    
    async def heartbeat(self):
        while 1:
            await asyncio.sleep(60)
            await self.ws_conn.send(DGWSMessage.HEARTBEAT)
    
    async def device_keepalive(self):
        """Send periodic low-power pulse to prevent device from sleeping when idle"""
        while 1:
            await asyncio.sleep(KEEPALIVE_INTERVAL)
            current_time = time.time()
            
            for channel in ['A', 'B']:
                # Check if channel has been idle long enough
                last_activity = LAST_ACTIVITY_TIME.get(channel, 0)
                idle_time = current_time - last_activity
                
                if idle_time >= KEEPALIVE_INTERVAL:
                    # Send very low power keep-alive signal
                    try:
                        # Set minimal strength (1 out of 200)
                        await self.set_strength(channel, mode='2', value=KEEPALIVE_POWER, force=True)
                        # Send minimal wave pattern
                        await self.send_wave(channel, wavestr=KEEPALIVE_WAVE)
                    except Exception:
                        pass
    
    async def connection_init(self):
        await asyncio.sleep(2)
        logger.info(f'Device {self.uuid[:8]} initializing channels...')
        await self.set_strength('A', value=1, force=True)
        await self.set_strength('B', value=1, force=True)
        logger.success(f'Device {self.uuid[:8]} channels initialized (A=1, B=1)')

    async def serve(self):
        logger.success(f'New WebSocket connection: Device {self.uuid[:8]}... (total: {len(WS_CONNECTIONS)})')
        msg = DGWSMessage('bind', clientId=str(self.uuid), targetId='', message='targetId')
        await msg.send(self)
        asyncio.create_task(self.connection_init())
        try:
            hb = asyncio.ensure_future(self.heartbeat())
            keepalive = asyncio.ensure_future(self.device_keepalive())
            async for message in self.ws_conn:
                event = json.loads(message)
                msg = DGWSMessage(**event)
                try:
                    await self.msg_handler(msg)
                except Exception as e:
                    logger.error(traceback.format_exc())
                    DGWSMessage('error',message='500')
            await self.ws_conn.wait_closed()
        finally:
            logger.warning(f'Device {self.uuid[:8]} disconnected (remaining: {len(WS_CONNECTIONS) - 1})')
            hb.cancel()
            keepalive.cancel()
            WS_CONNECTIONS.remove(self)

    @classmethod
    async def broadcast_wave(cls, channel='A', wavestr=DEFAULT_WAVE):
        for conn in WS_CONNECTIONS:
            conn : cls
            await conn.send_wave(channel=channel, wavestr=wavestr)

    @classmethod
    async def broadcast_clear_wave(cls, channel='A'):
        for conn in WS_CONNECTIONS:
            conn : cls
            await conn.clear_wave(channel=channel)
    
    @classmethod
    async def broadcast_strength_0_to_1(cls, channel='A', value=0):
        for conn in WS_CONNECTIONS:
            conn : cls
            await conn.set_strength_0_to_1(channel=channel, value=value)
    
    @classmethod
    async def broadcast_strength_with_limit(cls, channel='A', value_0_to_1=0, device_limit=100, allow_exceed=False):
        """Set strength with a specific device limit (ignores connection strength_limit)"""
        for conn in WS_CONNECTIONS:
            conn : cls
            await conn.set_strength_with_limit(channel=channel, value_0_to_1=value_0_to_1, device_limit=device_limit, allow_exceed=allow_exceed)
    
    async def send_wakeup_pulse(self, channel='A'):
        """Send a small pulse to wake up the device when power level changes"""
        try:
            # Set wake-up strength
            await self.set_strength(channel, mode='2', value=WAKEUP_POWER, force=True)
            # Send short wave pattern
            await self.send_wave(channel, wavestr=WAKEUP_WAVE)
        except Exception:
            pass
    
    @classmethod
    async def broadcast_wakeup_pulse(cls, channel='A'):
        """Send wake-up pulse to all connected devices"""
        for conn in WS_CONNECTIONS:
            conn : cls
            await conn.send_wakeup_pulse(channel=channel)