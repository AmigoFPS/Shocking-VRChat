import numpy as np
import collections
import random
from .base_handler import BaseHandler
import time, asyncio, math, json

from ..connector.coyotev3ws import DGConnection


# Global runtime settings that can be updated from GUI
RUNTIME_PATTERN_SETTINGS = {
    'A': {
        'pattern': 'PROXIMITY',  # PROXIMITY, IMPACT, RECOIL
        'device_limit': 100,     # Max device power (0-200)
        'sensitivity': 100,      # Response multiplier (0-200%)
        'threshold': 10,         # Min activation level (0-100%)
        'impact_boost_min': 0,   # Min random boost on impact (0-100)
        'impact_boost_max': 30,  # Max random boost on impact (0-100)
    },
    'B': {
        'pattern': 'PROXIMITY',
        'device_limit': 100,
        'sensitivity': 100,
        'threshold': 10,
        'impact_boost_min': 0,
        'impact_boost_max': 30,
    }
}


class ShockHandler(BaseHandler):
    def __init__(self, SETTINGS: dict, DG_CONN: DGConnection, channel_name: str) -> None:
        self.SETTINGS = SETTINGS
        self.DG_CONN = DG_CONN
        self.channel = channel_name.upper()
        self.shock_settings = SETTINGS['dglab3'][f'channel_{channel_name.lower()}']
        self.mode_config    = self.shock_settings['mode_config']

        # Always use unified handler for real-time pattern switching
        self._handler = self.handler_unified
        
        self.bg_wave_update_time_window = 0.1
        self.bg_wave_current_strength = 0
        self.bg_wave_base_strength = 0  # Base strength from distance
        self.bg_wave_boost_strength = 0  # Boost from velocity/acceleration

        self.touch_dist_arr = collections.deque(maxlen=20)

        self.to_clear_time    = 0
        self.is_cleared       = True
    
    def get_runtime_settings(self):
        """Get current runtime pattern settings for this channel"""
        return RUNTIME_PATTERN_SETTINGS.get(self.channel, {
            'pattern': 'PROXIMITY',
            'device_limit': 100,
            'sensitivity': 100,
            'threshold': 10,
            'impact_boost_min': 0,
            'impact_boost_max': 30,
        })
    
    def start_background_jobs(self):
        # logger.info(f"Channel: {self.channel}, background job started.")
        asyncio.ensure_future(self.clear_check())
        # Unified background wave feeder handles all patterns
        asyncio.ensure_future(self.unified_background_wave_feeder())

    def osc_handler(self, address, *args):
        val = self.param_sanitizer(args)
        asyncio.ensure_future(self._handler(val))

    async def clear_check(self):
        # logger.info(f'Channel {self.channel} started clear check.')
        sleep_time = 0.05
        while 1:
            await asyncio.sleep(sleep_time)
            current_time = time.time()
            # logger.debug(f"{str(self.is_cleared)}, {current_time}, {self.to_clear_time}")
            if not self.is_cleared and current_time > self.to_clear_time:
                self.is_cleared = True
                self.bg_wave_current_strength = 0
                self.touch_dist_arr.clear()
                await self.DG_CONN.broadcast_clear_wave(self.channel)
    
    async def feed_wave(self):
        raise NotImplemented
        sleep_time = 1
        while 1:
            await asyncio.sleep(sleep_time)
            await self.DG_CONN.broadcast_wave(channel=self.channel, wavestr=self.shock_settings['shock_wave'])

    async def set_clear_after(self, val):
        self.is_cleared = False
        self.to_clear_time = time.time() + val

    @staticmethod
    def generate_wave_100ms(freq, from_, to_):
        assert 0 <= from_ <= 1, "Invalid wave generate."
        assert 0 <= to_   <= 1, "Invalid wave generate."
        from_ = int(100*from_)
        to_   = int(100*to_)
        ret = ["{:02X}".format(freq)]*4
        delta = (to_ - from_) // 4
        ret += ["{:02X}".format(min(max(from_ + delta*i, 0),100)) for i in range(1,5,1)]
        ret = ''.join(ret)
        return json.dumps([ret],separators=(',', ':'))
    
    def normalize_distance(self, distance):
        out_distance = 0
        trigger_bottom = self.mode_config['trigger_range']['bottom']
        trigger_top = self.mode_config['trigger_range']['top']
        if distance > self.mode_config['trigger_range']['bottom']:
            out_distance = (
                    distance - trigger_bottom
                ) / (
                    trigger_top - trigger_bottom
                )
            out_distance = 1 if out_distance > 1 else out_distance
        return out_distance

    async def handler_unified(self, distance):
        """Unified handler that tracks both distance and derivatives for all patterns"""
        await self.set_clear_after(0.5)
        out_distance = self.normalize_distance(distance)
        self.bg_wave_base_strength = out_distance
        
        # Always track distance history for derivative computation
        if out_distance > 0:
            t = time.time()
            self.touch_dist_arr.append([t, out_distance])

    async def handler_distance(self, distance):
        await self.set_clear_after(0.5)
        self.bg_wave_current_strength = self.normalize_distance(distance)

    async def unified_background_wave_feeder(self):
        """Unified wave feeder that handles all patterns with real-time switching and dynamic power"""
        tick_time_window = self.bg_wave_update_time_window / 20
        next_tick_time = 0
        last_strength = 0
        last_device_power = 0
        last_raw_strength = 0
        last_time = time.time()
        
        # Impact detection state
        current_boost = 0  # Current random boost amount
        boost_decay_time = 3.0  # Seconds to fully decay the boost (slow decay)
        impact_threshold = 0.2  # Minimum raw strength increase to trigger impact
        
        while 1:
            current_time = time.time()
            if current_time < next_tick_time:
                await asyncio.sleep(tick_time_window)
                continue
            next_tick_time = current_time + self.bg_wave_update_time_window
            
            # Calculate time delta for proper decay
            time_delta = current_time - last_time
            last_time = current_time
            
            # Get current pattern settings
            runtime = self.get_runtime_settings()
            pattern = runtime.get('pattern', 'PROXIMITY')
            device_limit = runtime.get('device_limit', 100)  # 0-200
            sensitivity = runtime.get('sensitivity', 100) / 100.0  # Convert to multiplier (0-2)
            threshold = runtime.get('threshold', 10) / 100.0  # Convert to 0-1
            boost_min = runtime.get('impact_boost_min', 0)
            boost_max = runtime.get('impact_boost_max', 30)
            
            # Calculate raw strength based on pattern
            raw_strength = 0
            
            if pattern == 'PROXIMITY':
                # Pure distance-based
                raw_strength = self.bg_wave_base_strength
                
            elif pattern == 'IMPACT' and len(self.touch_dist_arr) >= 4:
                # Velocity-based strength
                _, velocity, _, _ = self.compute_derivative()
                # Normalize velocity (typical range 0-5, map to 0-1)
                raw_strength = min(1.0, abs(velocity) / 5.0)
                
            elif pattern == 'RECOIL' and len(self.touch_dist_arr) >= 4:
                # Acceleration-based strength
                _, _, acceleration, _ = self.compute_derivative()
                # Normalize acceleration (typical range 0-50, map to 0-1)
                raw_strength = min(1.0, abs(acceleration) / 50.0)
            
            # Detect impact - sudden increase in raw strength OR high velocity/acceleration
            strength_increase = raw_strength - last_raw_strength
            is_impact = strength_increase > impact_threshold or raw_strength > 0.5
            
            if is_impact and boost_max > 0 and current_boost < boost_max * 0.8:
                # Impact detected! Apply random boost
                random_boost = random.randint(boost_min, boost_max)
                current_boost = min(boost_max, current_boost + random_boost)
            
            # Time-based decay: decay over boost_decay_time seconds
            if current_boost > 0:
                # Calculate how much to decay based on elapsed time
                decay_amount = (boost_max / boost_decay_time) * time_delta
                current_boost = max(0, current_boost - decay_amount)
            
            last_raw_strength = raw_strength
            
            # Apply sensitivity multiplier
            scaled_strength = raw_strength * sensitivity
            
            # Apply threshold - only activate if above threshold
            if scaled_strength < threshold:
                current_strength = 0
            else:
                # Remap: threshold to 1.0 -> 0 to 1.0
                current_strength = (scaled_strength - threshold) / (1.0 - threshold + 0.001)
                current_strength = min(1.0, max(0, current_strength))
            
            self.bg_wave_current_strength = current_strength
            
            # Calculate effective device limit with boost (capped at 200)
            effective_limit = min(200, device_limit + int(current_boost))
            
            # Calculate actual device power (0 to effective_limit)
            device_power = int(current_strength * effective_limit)
            
            if current_strength == last_strength == 0:
                continue
            
            # Send wave pattern (controls the wave shape)
            wave = self.generate_wave_100ms(
                self.mode_config['distance']['freq_ms'], 
                last_strength, 
                current_strength
            )
            
            # IMPORTANT: Also update actual device power dynamically!
            # This makes the device actually change power based on input
            if device_power != last_device_power:
                await self.DG_CONN.broadcast_strength_with_limit(
                    self.channel, 
                    value_0_to_1=current_strength, 
                    device_limit=effective_limit
                )
                last_device_power = device_power
            
            last_strength = current_strength
            await self.DG_CONN.broadcast_wave(self.channel, wavestr=wave)

    async def distance_background_wave_feeder(self):
        tick_time_window = self.bg_wave_update_time_window / 20
        next_tick_time   = 0
        last_strength    = 0
        while 1:
            current_time = time.time()
            if current_time < next_tick_time:
                await asyncio.sleep(tick_time_window)
                continue
            next_tick_time = current_time + self.bg_wave_update_time_window
            current_strength = self.bg_wave_current_strength
            if current_strength == last_strength == 0:
                continue
            wave = self.generate_wave_100ms(
                self.mode_config['distance']['freq_ms'], 
                last_strength, 
                current_strength
            )
            last_strength = current_strength
            await self.DG_CONN.broadcast_wave(self.channel, wavestr=wave)
    
    async def send_shock_wave(self, shock_time, shockwave: str):
        shockwave_duration = (shockwave.count(',')+1) * 0.1
        send_times = math.ceil(shock_time // shockwave_duration)
        for _ in range(send_times):
            await self.DG_CONN.broadcast_wave(self.channel, wavestr=self.mode_config['shock']['wave'])
            await asyncio.sleep(shockwave_duration)
    
    async def handler_shock(self, distance):
        current_time = time.time()
        if distance > self.mode_config['trigger_range']['bottom'] and current_time > self.to_clear_time:
            shock_duration = self.mode_config['shock']['duration']
            await self.set_clear_after(shock_duration)
            pass
            asyncio.create_task(self.send_shock_wave(shock_duration, self.mode_config['shock']['wave']))

    async def handler_touch(self, distance):
        await self.set_clear_after(0.5)
        out_distance = self.normalize_distance(distance)
        if out_distance == 0:
            return
        t = time.time()
        self.touch_dist_arr.append([t,out_distance])
    
    def compute_derivative(self):
        data = self.touch_dist_arr
        if len(data) < 4:
            # logger.warning('At least 4 samples are required to calculate acc and jerk.')
            return 0, 0, 0, 0

        time_ = np.array([point[0] for point in data])
        distance = np.array([point[1] for point in data])

        window_size = 3
        distance = np.convolve(distance, np.ones(window_size) / window_size, mode='valid')
        time_ = time_[:len(distance)]

        velocity = np.gradient(distance, time_)
        acceleration = np.gradient(velocity, time_)
        jerk = np.gradient(acceleration, time_)
        # logger.success(f"{distance[-1]:9.4f} {velocity[-1]:9.4f} {acceleration[-1]:9.4f} {jerk[-1]:9.4f}")
        return distance[-1], velocity[-1], acceleration[-1], jerk[-1]

    async def touch_background_wave_feeder(self):
        tick_time_window = self.bg_wave_update_time_window / 20
        next_tick_time   = 0
        last_strength    = 0
        while 1:
            current_time = time.time()
            if current_time < next_tick_time:
                await asyncio.sleep(tick_time_window)
                continue
            next_tick_time = current_time + self.bg_wave_update_time_window
            n_derivative = self.mode_config['touch']['n_derivative']
            current_strength = self.compute_derivative()[n_derivative]
            derivative_params = self.mode_config['touch']['derivative_params'][n_derivative]
            current_strength = max(min(derivative_params['bottom'],abs(current_strength)),derivative_params['top'])/(derivative_params['top']-derivative_params['bottom'])

            self.bg_wave_current_strength = current_strength
            if current_strength == last_strength == 0:
                continue
            wave = self.generate_wave_100ms(
                self.mode_config['touch']['freq_ms'], 
                last_strength, 
                current_strength
            )
            last_strength = current_strength
            # await self.DG_CONN.broadcast_wave(self.channel, wavestr=wave)

