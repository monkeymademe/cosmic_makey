import math
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN
import time

class AnimationManager:
    import eyes_move
    import leftarm_up
    import leftarm_down
    import rightarm_up
    import rightarm_down

    def __init__(self, graphics, mask_red, mask_white, base_image):
        self.graphics = graphics
        self.mask_red = set(mask_red)  # Convert to set for fast lookup
        self.mask_white = set(mask_white)
        self.base_image = base_image
        
        # Animation parameters
        self.phase = 0
        self.stripe_width = 6.0
        self.width = 32  # Cosmic Unicorn width
        self.height = 32  # Cosmic Unicorn height
        
        # Define eye regions (left and right eyes)
        self.left_eye_region = [(12, 5), (13, 5), (12, 6), (13, 6)]
        self.right_eye_region = [(18, 5), (19, 5), (18, 6), (19, 6)]
        
        # Precompute base pens for static parts
        self.base_pen_map = {}
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.mask_red and (x, y) not in self.mask_white:
                    r, g, b = self.base_image[y][x]
                    self.base_pen_map[(x, y)] = self.graphics.create_pen(r, g, b)
        
        self.white_pen = self.graphics.create_pen(255, 255, 255)
        
        # Draw static parts (base + white) once at startup
        self.draw_static_base()
        
        self.current_color = (255, 0, 0)  # Default to red
    
    def from_hsv(self, h, s, v):
        """HSV to RGB helper function"""
        i = math.floor(h * 6.0)
        f = h * 6.0 - i
        v *= 255.0
        p = v * (1.0 - s)
        q = v * (1.0 - f * s)
        t = v * (1.0 - (1.0 - f) * s)

        i = int(i) % 6
        if i == 0:
            return int(v), int(t), int(p)
        if i == 1:
            return int(q), int(v), int(p)
        if i == 2:
            return int(p), int(v), int(t)
        if i == 3:
            return int(p), int(q), int(v)
        if i == 4:
            return int(t), int(p), int(v)
        if i == 5:
            return int(v), int(p), int(q)
    
    def draw_static_base(self):
        """Draw the static base image (white outline and base image)"""
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.mask_white:
                    self.graphics.set_pen(self.white_pen)
                    self.graphics.pixel(x, y)
                elif (x, y) not in self.mask_red:
                    self.graphics.set_pen(self.base_pen_map[(x, y)])
                    self.graphics.pixel(x, y)
    
    def draw_red(self):
        """Draw red animation - red pixels are solid red"""
        # Only draw the red pixels (static base is already drawn)
        for x, y in self.mask_red:
            self.graphics.set_pen(self.graphics.create_pen(255, 0, 0))
            self.graphics.pixel(x, y)
    
    def draw_rainbow(self):
        """Draw rainbow animation - red pixels cycle through rainbow colors"""
        phase_percent = self.phase / 15.0
        
        # Only draw the red pixels (static base is already drawn)
        for x, y in self.mask_red:
            hue = (x / self.width + self.phase / 30.0) % 1.0
            v = ((math.sin((x + y) / self.stripe_width + phase_percent) + 1.5) / 2.5)
            r, g, b = self.from_hsv(hue, 1.0, v)
            pen = self.graphics.create_pen(r, g, b)
            self.graphics.set_pen(pen)
            self.graphics.pixel(x, y)
    
    def draw_fire(self):
        """Draw fire-like animation - red pixels flicker like fire with orange/yellow colors"""
        # Only draw the red pixels (static base is already drawn)
        for x, y in self.mask_red:
            # Create fire effect with multiple sine waves for realistic flickering
            base_intensity = (math.sin((x + y) / 3.0 + self.phase / 15.0) + 1.0) / 2.0
            flicker = (math.sin(self.phase / 8.0 + x * 0.5) + 1.0) / 2.0
            wave = (math.sin((x + y) / 2.0 + self.phase / 20.0) + 1.0) / 2.0
            
            # Combine effects for realistic fire
            intensity = (base_intensity * 0.6 + flicker * 0.3 + wave * 0.1)
            intensity = max(0.3, min(1.0, intensity))  # Keep fire bright
            
            # Fire colors: red to orange to yellow
            if intensity > 0.8:
                # Yellow/orange tip of flame
                r = int(255 * intensity)
                g = int(200 * intensity)
                b = int(50 * intensity)
            elif intensity > 0.6:
                # Orange middle
                r = int(255 * intensity)
                g = int(150 * intensity)
                b = int(30 * intensity)
            else:
                # Red base
                r = int(255 * intensity)
                g = int(80 * intensity)
                b = int(20 * intensity)
            
            self.graphics.set_pen(self.graphics.create_pen(r, g, b))
            self.graphics.pixel(x, y)
    
    def draw_eyes_moving(self):
        """
        Draw only one frame of the eyes animation per call, drawing on top of the existing display.
        Advances frame index each time it's called.
        Extra debug: print frame index before/after.
        Display update is handled by main loop.
        """
        if not hasattr(self, '_eyes_frame_index'):
            self._eyes_frame_index = 0
        print(f"[DEBUG] Current frame index: {self._eyes_frame_index}")
        frame_data = eyes_move.animation_frames[self._eyes_frame_index]
        print(f"Drawing frame {self._eyes_frame_index}")
        print(f"  red_pixels: {frame_data['red_pixels']}")
        print(f"  white_pixels: {frame_data['white_pixels']}")
        # Draw eye pixels as white
        for x, y in frame_data['white_pixels']:
            self.graphics.set_pen(self.white_pen)
            self.graphics.pixel(x, y)
        # Draw colored pixels for eyes
        for x, y in frame_data['red_pixels']:
            pen = self.graphics.create_pen(*self.current_color)
            self.graphics.set_pen(pen)
            self.graphics.pixel(x, y)
        # Advance to next frame for next call
        self._eyes_frame_index = (self._eyes_frame_index + 1) % len(eyes_move.animation_frames)
        print(f"[DEBUG] Next frame index will be: {self._eyes_frame_index}")
    
    def run_eyes_moving(self, repeat=2, frame_delay_ms=33):
        """
        Run the eyes moving animation for all frames, 'repeat' times, then stop.
        Handles display update and timing internally.
        """
        pass
    
    def update_rainbow_phase(self):
        """Update the rainbow animation phase - call this each frame"""
        self.phase += 1
        if self.phase > 10000:  # Wrap to avoid large numbers
            self.phase = 0
    
    def reset_phase(self):
        """Reset animation phase to 0"""
        self.phase = 0
        self.eye_phase = 0
        self.eye_blink_phase = 0
    
    def set_stripe_width(self, width):
        """Set the stripe width for rainbow animation"""
        self.stripe_width = width
    
    def get_phase(self):
        """Get current animation phase"""
        return self.phase
    
    def set_mask_color(self, color_name):
        """Set the current color for mask and eyes animation."""
        color_map = {
            "red": (255, 0, 0),
            "blue": (0, 0, 255),
            "green": (0, 255, 0),
            "purple": (128, 0, 128),
            "pink": (255, 105, 180)
        }
        self.current_color = color_map.get(color_name, (255, 0, 0))

    def draw_mask_color(self):
        """Draw the mask in the current color."""
        for x, y in self.mask_red:
            self.graphics.set_pen(self.graphics.create_pen(*self.current_color))
            self.graphics.pixel(x, y)
    
    def draw_laugh(self):
        """
        Draw only one frame of the laugh animation per call, drawing on top of the existing display.
        Advances frame index each time it's called.
        Display update is handled by main loop.
        """
        from laugh import animation_frames  # Import inside function for latest arrays
        if not hasattr(self, '_laugh_frame_index'):
            self._laugh_frame_index = 0
        print(f"[DEBUG] Current laugh frame index: {self._laugh_frame_index}")
        frame_data = animation_frames[self._laugh_frame_index]
        print(f"Drawing laugh frame {self._laugh_frame_index}")
        print(f"  red_pixels: {frame_data['red_pixels']}")
        print(f"  white_pixels: {frame_data['white_pixels']}")
        # Draw laugh pixels as white
        for x, y in frame_data['white_pixels']:
            self.graphics.set_pen(self.white_pen)
            self.graphics.pixel(x, y)
        # Draw colored pixels for laugh
        for x, y in frame_data['red_pixels']:
            pen = self.graphics.create_pen(*self.current_color)
            self.graphics.set_pen(pen)
            self.graphics.pixel(x, y)
        # Advance to next frame for next call
        self._laugh_frame_index = (self._laugh_frame_index + 1) % len(animation_frames)
        print(f"[DEBUG] Next laugh frame index will be: {self._laugh_frame_index}")

    def draw_leftarm_up(self):
        if not hasattr(self, '_leftarm_up_frame_index'):
            self._leftarm_up_frame_index = 0

        frame_data = leftarm_up.animation_frames[self._leftarm_up_frame_index]

        # --- STEP 1: Black out the arm area ---
        black_pen = self.graphics.create_pen(0, 0, 0)
        ARM_X1, ARM_X2 = 0, 8   # change to your exact bounding box
        ARM_Y1, ARM_Y2 = 0, 26
        for y in range(ARM_Y1, ARM_Y2 + 1):
            for x in range(ARM_X1, ARM_X2 + 1):
                self.graphics.set_pen(black_pen)
                self.graphics.pixel(x, y)

        # --- STEP 2: Draw white pixels ---
        for x, y in frame_data['white_pixels']:
            self.graphics.set_pen(self.white_pen)
            self.graphics.pixel(x, y)

        # --- STEP 3: Draw red (or current color) pixels ---
        for x, y in frame_data['red_pixels']:
            pen = self.graphics.create_pen(*self.current_color)
            self.graphics.set_pen(pen)
            self.graphics.pixel(x, y)

        # --- STEP 4: Advance animation frame ---
        self._leftarm_up_frame_index = (
            self._leftarm_up_frame_index + 1
        ) % len(leftarm_up.animation_frames)

    def draw_leftarm_down(self):
        from leftarm_down import animation_frames
        if not hasattr(self, '_leftarm_down_frame_index'):
            self._leftarm_down_frame_index = 0

        frame_data = animation_frames[self._leftarm_down_frame_index]

        # --- STEP 1: Black out the arm area ---
        black_pen = self.graphics.create_pen(0, 0, 0)
        ARM_X1, ARM_X2 = 0, 8   # change to your exact bounding box
        ARM_Y1, ARM_Y2 = 0, 26
        for y in range(ARM_Y1, ARM_Y2 + 1):
            for x in range(ARM_X1, ARM_X2 + 1):
                self.graphics.set_pen(black_pen)
                self.graphics.pixel(x, y)

        # --- STEP 2: Draw white pixels ---
        for x, y in frame_data['white_pixels']:
            self.graphics.set_pen(self.white_pen)
            self.graphics.pixel(x, y)

        # --- STEP 3: Draw red (or current color) pixels ---
        for x, y in frame_data['red_pixels']:
            pen = self.graphics.create_pen(*self.current_color)
            self.graphics.set_pen(pen)
            self.graphics.pixel(x, y)

        # --- STEP 4: Advance animation frame ---
        self._leftarm_down_frame_index = (
            self._leftarm_down_frame_index + 1
        ) % len(animation_frames)
        
        
        
    def draw_rightarm_up(self):
        from rightarm_up import animation_frames
        if not hasattr(self, '_rightarm_up_frame_index'):
            self._rightarm_up_frame_index = 0

        frame_data = animation_frames[self._rightarm_up_frame_index]

        # --- STEP 1: Black out the arm area ---
        black_pen = self.graphics.create_pen(0, 0, 0)
        ARM_X1, ARM_X2 = 23, 32   # change to your exact bounding box
        ARM_Y1, ARM_Y2 = 0, 26
        for y in range(ARM_Y1, ARM_Y2 + 1):
            for x in range(ARM_X1, ARM_X2 + 1):
                self.graphics.set_pen(black_pen)
                self.graphics.pixel(x, y)

        # --- STEP 2: Draw white pixels ---
        for x, y in frame_data['white_pixels']:
            self.graphics.set_pen(self.white_pen)
            self.graphics.pixel(x, y)

        # --- STEP 3: Draw red (or current color) pixels ---
        for x, y in frame_data['red_pixels']:
            pen = self.graphics.create_pen(*self.current_color)
            self.graphics.set_pen(pen)
            self.graphics.pixel(x, y)

        # --- STEP 4: Advance animation frame ---
        self._rightarm_up_frame_index = (
            self._rightarm_up_frame_index + 1
        ) % len(animation_frames)

    def draw_rightarm_down(self):
        from rightarm_down import animation_frames
        if not hasattr(self, '_rightarm_down_frame_index'):
            self._rightarm_down_frame_index = 0

        frame_data = animation_frames[self._rightarm_down_frame_index]

        # --- STEP 1: Black out the arm area ---
        black_pen = self.graphics.create_pen(0, 0, 0)
        ARM_X1, ARM_X2 = 23, 32   # change to your exact bounding box
        ARM_Y1, ARM_Y2 = 0, 26
        for y in range(ARM_Y1, ARM_Y2 + 1):
            for x in range(ARM_X1, ARM_X2 + 1):
                self.graphics.set_pen(black_pen)
                self.graphics.pixel(x, y)

        # --- STEP 2: Draw white pixels ---
        for x, y in frame_data['white_pixels']:
            self.graphics.set_pen(self.white_pen)
            self.graphics.pixel(x, y)

        # --- STEP 3: Draw red (or current color) pixels ---
        for x, y in frame_data['red_pixels']:
            pen = self.graphics.create_pen(*self.current_color)
            self.graphics.set_pen(pen)
            self.graphics.pixel(x, y)

        # --- STEP 4: Advance animation frame ---
        self._rightarm_down_frame_index = (
            self._rightarm_down_frame_index + 1
        ) % len(animation_frames)

    def draw_dance_1(self):
        from dance_1 import animation_frames
        if not hasattr(self, '_dance_1_frame_index'):
            self._dance_1_frame_index = 0

        frame_data = animation_frames[self._dance_1_frame_index]

        # --- Pre-create pens ---
        black_pen = self.graphics.create_pen(0, 0, 0)
        white_pen = self.white_pen
        red_pen = self.graphics.create_pen(*self.current_color)

        # --- STEP 1: Black out left arm area ---
        ARM_X1, ARM_X2 = 0, 8
        ARM_Y1, ARM_Y2 = 0, 26
        self.graphics.set_pen(black_pen)
        for y in range(ARM_Y1, ARM_Y2 + 1):
            for x in range(ARM_X1, ARM_X2 + 1):
                self.graphics.pixel(x, y)

        # --- STEP 2: Black out right arm area ---
        ARM_X1, ARM_X2 = 23, 31
        ARM_Y1, ARM_Y2 = 0, 26
        self.graphics.set_pen(black_pen)
        for y in range(ARM_Y1, ARM_Y2 + 1):
            for x in range(ARM_X1, ARM_X2 + 1):
                self.graphics.pixel(x, y)

        # --- STEP 3: Draw white pixels ---
        self.graphics.set_pen(white_pen)
        for x, y in frame_data['white_pixels']:
            self.graphics.pixel(x, y)

        # --- STEP 4: Draw red (or current color) pixels ---
        self.graphics.set_pen(red_pen)
        for x, y in frame_data['red_pixels']:
            self.graphics.pixel(x, y)

        # --- STEP 5: Advance animation frame ---
        self._dance_1_frame_index = (
            self._dance_1_frame_index + 1
        ) % len(animation_frames)

