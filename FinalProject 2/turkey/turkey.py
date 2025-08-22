import pygame
import os
import sys
import random
from math import *
from pygame.locals import *
from sys import exit

class Main(object):
    def __init__(self):
        pygame.init()
        self.size = (800, 600)
        self.screen = pygame.display.set_mode(self.size, 0, 32)

        

       # Keep original full-res so we can make a crisp big portrait
        self.boss_head_full = pygame.image.load("Turkethimus.png").convert_alpha()
        self.boss_head = pygame.transform.scale(self.boss_head_full, (100, 100))   # sprite-size
        self.boss_portrait_base = pygame.transform.smoothscale(self.boss_head_full, (240, 240))  # dialogue portrait

        self.dialogue_font = pygame.font.SysFont(None, 32)
        self.boss_dialogue = ""
        self.dialogue_timer = 0

        pygame.display.set_caption("Mmmmm Gobble, gobble")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)
        self.dialogue_font = getattr(self, "dialogue_font", pygame.font.SysFont(None, 32))
        self.name_font = pygame.font.SysFont(None, 36)
        self.text_color = (255, 255, 255)

        # fist image for punching turkeys. EH
        self.fist_open = pygame.image.load("fist.png").convert_alpha()
        self.fist_open = pygame.transform.scale(self.fist_open, (64, 64))

        # full-res fist image for dialogue portrait
        try:
            self.fist_full = pygame.image.load("fist.png").convert_alpha() 
        except pygame.error:
            self.fist_full = self.fist_open  # fallback

        # Erika's meme sounds and images added below. EH
        pygame.mixer.music.load("goofygoober.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.gobble_sound = pygame.mixer.Sound("erikaturkeyscream.wav")
        self.heaven_sound = pygame.mixer.Sound("heaven.wav")
        self.turkdeath = pygame.image.load("deadturk.png").convert_alpha()
        self.celebrated = False
        self.dialogue_triggered = False

        self.dialogue_active = False                                              
        self.dialogue_lines = []                                               
        self.dialogue_idx = 0                                               
        self.dialogue_char = 0                                                   
        self.dialogue_speed = 45  # chars per second                        
        self.dialogue_last_tick = 0                                            
        self.dialogue_pause_until = 0                                            
        self.dialogue_box = pygame.Surface((self.size[0] - 80, 180), pygame.SRCALPHA)
        self.dialogue_box_pos = (40, self.size[1] - 200)

        # universal punch sfx for all hits. EH
        self.punch_sound = pygame.mixer.Sound("punch.mp3")
        self.punch_sound.set_volume(0.8)  # volume
        pygame.mixer.set_num_channels(32)  # set number of channels for sound effects. EH
        # Turkethimus boss damage sfx added below. EH
        self.boss_damage_sfx = pygame.mixer.Sound("Bossdamage.wav")
        self.boss_damage_sfx.set_volume(1.0)
        self.boss_chan = pygame.mixer.Channel(4)
        self.boss_chan.set_volume(1.0)
        # --- Turkethimus dialogue voice ---
        self.turk_voice_files = ["turkethimustalk.wav"]
        self.turk_voice = []
        for fn in self.turk_voice_files:
            try:
                s = pygame.mixer.Sound(fn)
                s.set_volume(0.95)  # loud and clear
                self.turk_voice.append(s)
            except pygame.error:
                pass

        self.voice_chan = pygame.mixer.Channel(5)  # dedicated voice channel
        self.voice_started_line = False            # reset each new line

        self.turkeys = pygame.sprite.Group()
        self.roasts = pygame.sprite.Group()
        self.bosses = pygame.sprite.Group()
        self.boss_spawned = False
        for i in range(6):
            x = random.randint(100, 700)
            y = random.randint(100, 500)
            self.turkeys.add(Turkey((x,y)))

        self.background = pygame.Surface(self.size, 0, 32)
        self.b_ground = pygame.image.load("table.jpg")

        self.menu_bg = pygame.image.load("reallyscaryturkey.png").convert()
        self.menu_bg = pygame.transform.smoothscale(self.menu_bg, self.size)

        # initialize game state and start menu buttons. MK
        self.game_state = "menu"  # ensure start at menu state. MK
        pygame.mouse.set_visible(True)  # ensure mouse is visible in menu. EH
        self.button_font = pygame.font.SysFont(None, 48)
        # two button 'Start' and 'Quit' created and positioned. MK
        self.buttons = [
            Button(
                "Start",
                (300, 250),
                (200, 60),
                self.button_font,
                (100, 100, 100),
                (150, 150, 150),
            ),
            Button(
                "Quit",
                (300, 350),
                (200, 60),
                self.button_font,
                (100, 100, 100),
                (150, 150, 150),
            )
        ]

        # method for menu. MK
    def show_menu(self):
        pygame.mouse.set_visible(True)  # ensure mouse is visible in menu. EH
        # display menu. MK
        title_text = self.font.render("Mmmmm Gobble, Gobble", True, self.text_color)
        title_rect = title_text.get_rect(center=(400, 100))
        self.screen.blit(self.menu_bg, (0, 0))
        self.screen.blit(title_text, title_rect)

        for button in self.buttons:
            button.draw(self.screen)

        pygame.display.flip()

        # handle menu events. MK
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            for button in self.buttons:
                if button.is_clicked(event):
                    if button.text == "Start":
                        self.game_state = "game"  # switch to game state. MK
                        pygame.mouse.set_visible(False)  # hide mouse in game state. EH
                    elif button.text == "Quit":
                        pygame.quit()
                        sys.exit()
    def start_dialogue(self):                                           
        # Freeze gameplay and set state                                
        self.game_state = "dialogue"                                  
        self.dialogue_active = True                                   
        self.dialogue_idx = 0
        if self.voice_chan.get_busy():
            self.voice_chan.stop()
        self.voice_started_line = False                                     
        self.dialogue_char = 0                                         
        now = pygame.time.get_ticks()                                
        self.dialogue_last_tick = now                               
        self.dialogue_pause_until = now + 1000  # 1s suspense pause        

        # Lines: (speaker, text)                                  
        self.dialogue_lines = [                                            
            ("Turkethimus", "So… you devoured my flock and think the feast ENDS HERE?!?!"),  
            ("Hand",        "That was the appetizer. Your time is up, Turkethimus."),     
            ("Turkethimus", "Hah! Then come, little hand. Let fate carve the winner."), 
            ("Hand",        "I will roast you like the rest of your flock!"),              
        ]                                                                   

    def start_line_voice(self, speaker):
        if speaker == "Turkethimus" and self.turk_voice:
            snd = random.choice(self.turk_voice)
            self.voice_chan.play(snd)

    def draw_dialogue(self):
        if not self.dialogue_lines or self.dialogue_idx >= len(self.dialogue_lines):
            self.dialogue_active = False
            self.game_state = "game"
            if self.voice_chan.get_busy():
                self.voice_chan.stop()
            self.voice_started_line = False
            return                                               
        # Draw current scene (frozen)                                      
        self.background.fill((255, 255, 255))                        
        self.background.blit(self.b_ground, (0, 0))                        
        self.roasts.draw(self.background)                                 
        self.turkeys.draw(self.background)                              
        self.bosses.draw(self.background)                                

        # Darken the screen                                                
        overlay = pygame.Surface(self.size, pygame.SRCALPHA)               
        overlay.fill((0, 0, 0, 140))                                   
        self.background.blit(overlay, (0, 0))                              
        now = pygame.time.get_ticks()                                
        if now < self.dialogue_pause_until:                                
            self.screen.blit(self.background, (0, 0))                 
            pygame.display.flip()                                          
            return                                                   

        # Typewriter advance                                             
        dt = (now - self.dialogue_last_tick) / 1000.0          
        self.dialogue_last_tick = now                                      

        speaker, full_text = self.dialogue_lines[self.dialogue_idx]
        # Added Big Turkethimus head during dialogue. EH
        if speaker == "Turkethimus":
            # Added gentle “breathing” pulse. EH
            pulse = 1.0 + 0.04 * sin(pygame.time.get_ticks() / 250.0)
            base = 240
            w = int(base * pulse); h = int(base * pulse)

            # Scale from the full-res head for crispness
            portrait = pygame.transform.smoothscale(self.boss_head_full, (w, h))

            # Position near the bottom-left, just above the dialogue box
            # (box top-left is at self.dialogue_box_pos = (40, H-200))
            px = 40
            py = self.size[1] - 200 - h + 10   # a little overlap looks nice
            self.background.blit(portrait, (px, py))
        if speaker == "Hand":
            pulse = 1.0 + 0.04 * sin(pygame.time.get_ticks() / 250.0)
            base = 220
            w = int(base * pulse); h = int(base * pulse)
            src = getattr(self, "fist_full", self.fist_open)       # falls back to fist_open
            fist_portrait = pygame.transform.smoothscale(src, (w, h))
            px = self.size[0] - w - 40
            py = self.size[1] - 200 - h + 10
            self.background.blit(fist_portrait, (px, py))
        # start voice once per line when characters begin appearing
        if not self.voice_started_line and self.dialogue_char == 0:
            self.start_line_voice(speaker)
            self.voice_started_line = True  

        if self.dialogue_char < len(full_text):                            
            self.dialogue_char = min(len(full_text),                       
                                     self.dialogue_char + int(self.dialogue_speed * dt))  

        shown = full_text[:self.dialogue_char]                             

        # Dialogue box                                               
        self.dialogue_box.fill((0, 0, 0, 180))                             
        box = self.dialogue_box.get_rect(topleft=self.dialogue_box_pos)    
        self.background.blit(self.dialogue_box, box)                       

        # Speaker label                                                    
        name_surf = self.name_font.render(speaker + ":", True, (255, 220, 160))  
        self.background.blit(name_surf, (box.x + 16, box.y + 14))          
        # Wrapped text                                                
        x, y = box.x + 16, box.y + 52                                 
        max_w = box.width - 32                                         
        line = ""                                                      
        for w in shown.split(" "):                                    
            test = (line + " " + w).strip()                           
            if self.dialogue_font.size(test)[0] <= max_w:             
                line = test                                          
            else:                                                          
                self.background.blit(self.dialogue_font.render(line, True, (255, 255, 255)), (x, y))  
                y += 32                                                    
                line = w                                             
        if line:                                                           
            self.background.blit(self.dialogue_font.render(line, True, (255, 255, 255)), (x, y))  

        # Hint when the line is finished                                
        if self.dialogue_char >= len(full_text):                       
            hint = self.dialogue_font.render("Press Space or Click to continue…", True, (200, 200, 200))  
            self.background.blit(hint, (box.right - hint.get_width() - 16, box.bottom - 36))  

        self.screen.blit(self.background, (0, 0))                          
        pygame.display.flip()                                              
    def main(self):
        while True:
            # Gate by state: render and handle the title menu until Start, then fall through to gameplay. EH
            if self.game_state == "menu":
                self.clock.tick(60)
                self.show_menu()
                continue

            # -- DIALOGUE --                                     
            if self.game_state == "dialogue":                         
                for event in pygame.event.get():                    
                    if event.type == QUIT:                          
                        pygame.quit(); sys.exit()                           
                    if event.type == KEYDOWN and event.key == K_ESCAPE:    
                        pygame.quit()
                        sys.exit()                                              
                    # ignore input during suspense pause                   
                    if pygame.time.get_ticks() < self.dialogue_pause_until:  
                        continue                                            
                    if event.type in (KEYDOWN, MOUSEBUTTONDOWN):           
                        speaker, full_text = self.dialogue_lines[self.dialogue_idx]  
                        if self.dialogue_char < len(full_text):            
                            # finish current line instantly                 
                            self.dialogue_char = len(full_text)            
                        else:
                            # stop the current voice and reset so the next line can trigger sound
                            if self.voice_chan.get_busy():
                                self.voice_chan.stop()
                            self.voice_started_line = False

                            # next line or end
                            self.dialogue_idx += 1
                            self.dialogue_char = 0
                            if self.dialogue_idx >= len(self.dialogue_lines):
                                self.dialogue_active = False
                                self.game_state = "game"
                                # clean up voice on exit
                                if self.voice_chan.get_busy():
                                    self.voice_chan.stop()
                                self.voice_started_line = False
                            else:
                                self.dialogue_last_tick = pygame.time.get_ticks()  
                self.draw_dialogue()                                       
                continue  
                                                             
            # --- Event handling (mouse clicks must be handled here) ---
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # Handle left mouse clicks here (inside event loop)
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    # click turkeys
                    for t in list(self.turkeys):
                        if t.rect.collidepoint(event.pos):
                            self.punch_sound.play() # play punch sound on turkey hit. EH
                            pos = t.rect.center
                            t.kill()
                            self.roasts.add(Roast(pos))
                            self.gobble_sound.play()
                            break
                    # click boss
                    for boss in list(self.bosses):
                        if boss.rect.collidepoint(event.pos):
                            self.punch_sound.play() # play punch sound on boss hit. EH
                            self.boss_chan.play(self.boss_damage_sfx)  # play boss damage sound. EH
                            boss.health -= 1
                            print(f"Turkethimus HP: {boss.health}")
                            if boss.health <= 0:
                                boss.kill()
                                pygame.mixer.music.stop()
                                self.heaven_sound.play()
                                self.celebrated = True

            # --- Game update & drawing ---
            self.clock.tick(60)
            self.background.fill((255,255,255))
            self.background.blit(self.b_ground, (0,0))

            self.m_pos = pygame.mouse.get_pos()

            self.turkeys.update()
            self.roasts.update()
            self.bosses.update()

            # spawn boss when turkeys are gone
            if len(self.turkeys) == 0 and not self.boss_spawned:
                self.bosses.add(BossTurkey((400, 300)))
                self.boss_spawned = True
                pygame.mixer.music.load("bossturkeytheme.mp3")
                pygame.mixer.music.play(-1)

            # Trigger dialogue once after the flock is cleared and boss is up 
            if len(self.turkeys) == 0 and self.boss_spawned and not self.dialogue_triggered and len(self.bosses) > 0:  
                self.dialogue_triggered = True                                   
                self.start_dialogue()                                            
                continue  # dialogue branch will handle drawing                     

            # draw everything to the background
            self.roasts.draw(self.background)
            self.turkeys.draw(self.background)
            self.bosses.draw(self.background)

            # --- Health bar display for Turkethimus ---
            for boss in self.bosses:
                bar_width = 60
                bar_height = 10
                bar_x = boss.rect.centerx - bar_width // 2
                bar_y = boss.rect.top - 20

                # Draw black border
                pygame.draw.rect(self.background, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)

                # Calculate health ratio
                health_ratio = boss.health / 5  # max health = 5

                # Draw red health fill
                fill_width = int(bar_width * health_ratio)
                if fill_width > 0:
                    pygame.draw.rect(self.background, (255, 0, 0), (bar_x + 1, bar_y + 1, fill_width - 2, bar_height - 2))

            # Celebration visuals
            if self.celebrated:
            # scale down to ~85% so it looks “zoomed out”
                scale = 0.85
                w, h = self.turkdeath.get_size()
                img_small = pygame.transform.smoothscale(self.turkdeath, (int(w*scale), int(h*scale)))
                rect = img_small.get_rect(center=(400, 300))
                self.background.blit(img_small, rect)

                victory_text = self.font.render("Have a Big Back Thanksgiving", True, self.text_color)
                text_rect = victory_text.get_rect(center=(400, 500))
                self.background.blit(victory_text, text_rect)
            # Draw fist reticle on top. EH
            mx, my = pygame.mouse.get_pos()
            fist_img = self.fist_open if pygame.mouse.get_pressed()[0] else self.fist_open
            fist_rect = fist_img.get_rect(center=(mx, my))
            self.background.blit(fist_img, fist_rect)
            self.screen.blit(self.background, (0,0))
            pygame.display.flip()

class Button:
    def __init__(self, text, pos, size, font, color, hover_color):
        # button properties. MK
        self.text = text
        self.pos = pos
        self.size = size
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.rect = pygame.Rect(pos, size)
        self.text_surface = self.font.render(self.text, True, (255, 255, 255))
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, surface):
        # button with hover effect. MK
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, self.hover_color, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
        surface.blit(self.text_surface, self.text_rect)

    def is_clicked(self, event):
        # check if button is clicked. MK
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
            return False


class Turkey(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("turkey.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)

        # chaos dial (raise to 1.2 for a bit faster, lower to 0.8 for slower) EH
        self.chaos = 1.0

        # movement knobs EH
        self.base_speed_min = 1.4 * self.chaos
        self.base_speed_max = 3.2 * self.chaos
        self.speed_cap      = 6.0 * self.chaos
        self.dash_speed     = 9.0 * self.chaos
        self.turn_jitter    = 1.0            # radians added on a turn
        self.frame_jitter   = 0.35           # per frame wobble
        self.edge_kick      = 3.5            # bounce push from edges

        # heading and velocity EH
        self.angle = random.uniform(0, 2*pi)
        self.speed = random.uniform(self.base_speed_min, self.base_speed_max)
        self.vx = cos(self.angle) * self.speed
        self.vy = sin(self.angle) * self.speed

        now = pygame.time.get_ticks()
        self.next_turn_at = now + random.randint(200, 450)
        self.dashing = False
        self.dash_end_at = 0
        self.next_dash_at = now + random.randint(1100, 2000)

    def _clamp_speed(self, cap):
        mag = hypot(self.vx, self.vy)
        if mag < 1e-6:
            self.vx, self.vy = 1.0, 0.0
            return
        if mag > cap:
            k = cap / mag
            self.vx *= k; self.vy *= k

    def _start_dash(self, now):
        self.dashing = True
        self.dash_end_at = now + random.randint(140, 220)
        self.angle += random.uniform(-pi, pi)   # quick flip
        self.vx = cos(self.angle) * self.dash_speed
        self.vy = sin(self.angle) * self.dash_speed

    def update(self):
        now = pygame.time.get_ticks()

        # periodic turns EH
        if now >= self.next_turn_at and not self.dashing:
            self.angle += random.uniform(-self.turn_jitter, self.turn_jitter)
            self.speed = random.uniform(self.base_speed_min, self.base_speed_max)
            self.vx += cos(self.angle) * self.speed
            self.vy += sin(self.angle) * self.speed
            self.next_turn_at = now + random.randint(200, 450)

        # dash bursts EH
        if self.dashing:
            if now >= self.dash_end_at:
                self.dashing = False
                self.next_dash_at = now + random.randint(1100, 2000)
        else:
            if now >= self.next_dash_at:
                self._start_dash(now)

        # light wobble EH
        self.vx += random.uniform(-self.frame_jitter, self.frame_jitter)
        self.vy += random.uniform(-self.frame_jitter, self.frame_jitter)

        # clamp EH
        self._clamp_speed(self.dash_speed if self.dashing else self.speed_cap)

        # move EH
        x, y = self.rect.center
        x += self.vx
        y += self.vy

        # bounce edges with a small kick
        if x <= 0:
            x = 0; self.vx = abs(self.vx) + self.edge_kick
            self.angle = atan2(self.vy, self.vx)
        elif x >= 800:
            x = 800; self.vx = -abs(self.vx) - self.edge_kick
            self.angle = atan2(self.vy, self.vx)

        if y <= 0:
            y = 0; self.vy = abs(self.vy) + self.edge_kick
            self.angle = atan2(self.vy, self.vx)
        elif y >= 600:
            y = 600; self.vy = -abs(self.vy) - self.edge_kick
            self.angle = atan2(self.vy, self.vx)

        self.rect.center = (x, y)


class BossTurkey(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("Turkethimus.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(center=pos)
        self.rect.center = pos

        self.health = 5  # takes 5 hits to kill
        self.last_health = self.health  # used to detect changes once

        # aggression and twitch knobs
        self.max_speed = 7.0          # normal top speed
        self.dash_speed = 12.0        # speed during dash
        self.seek_accel = 0.20        # how strongly he hunts the cursor
        self.evade_radius = 120       # if cursor gets this close, he dodges
        self.evade_accel = 0.90
        self.frame_jitter = 0.25      # tiny random wobble
        self.zigzag_amp = 0.55        # lateral sway amount
        self.zigzag_freq = random.uniform(6.0, 9.0)  # sway speed

        # dash timing
        now = pygame.time.get_ticks()
        self.next_dash_at = now + random.randint(900, 1600)
        self.dashing = False
        self.dash_end_at = 0
        self.telegraph_ms = 150       # brief flash before dash

        # velocity and time base
        angle = random.uniform(0, 2*pi)
        speed = random.uniform(2.0, 3.5)
        self.vx = cos(angle) * speed
        self.vy = sin(angle) * speed
        self.t0 = now

    def update(self):
        now = pygame.time.get_ticks()
        t = (now - self.t0) / 1000.0

        mx, my = pygame.mouse.get_pos()
        bx, by = self.rect.center
        tx = mx - bx
        ty = my - by
        dist = max(1e-6, hypot(tx, ty))

        # telegraph a dash by flashing alpha
        if not self.dashing and now >= self.next_dash_at - self.telegraph_ms:
            self.image.set_alpha(140)
        else:
            self.image.set_alpha(255)

        if self.dashing:
            if now >= self.dash_end_at:
                self.dashing = False
        else:
            # seek the cursor from far away
            self.vx += (tx / dist) * self.seek_accel
            self.vy += (ty / dist) * self.seek_accel

            # if the cursor is very close, dodge away to avoid easy clicks
            if dist < self.evade_radius:
                self.vx -= (tx / dist) * self.evade_accel
                self.vy -= (ty / dist) * self.evade_accel

            # add lateral zigzag perpendicular to the target direction
            px, py = -ty / dist, tx / dist  # unit perpendicular
            sway = sin(self.zigzag_freq * t) * self.zigzag_amp
            self.vx += px * sway
            self.vy += py * sway

            # small random twitch each frame
            self.vx += random.uniform(-self.frame_jitter, self.frame_jitter)
            self.vy += random.uniform(-self.frame_jitter, self.frame_jitter)

            # start a dash straight at the cursor on a timer
            if now >= self.next_dash_at:
                self.dashing = True
                self.dash_end_at = now + random.randint(200, 320)
                self.next_dash_at = now + random.randint(900, 1600)
                self.vx = (tx / dist) * self.dash_speed
                self.vy = (ty / dist) * self.dash_speed

        # clamp speed
        cap = self.dash_speed if self.dashing else self.max_speed
        speed = hypot(self.vx, self.vy)
        if speed > cap:
            k = cap / speed
            self.vx *= k; self.vy *= k

        # move
        x = bx + self.vx
        y = by + self.vy

        # bounce walls with a tiny kick so he does not stick
        if x <= 0:
            x = 0; self.vx = abs(self.vx) + random.uniform(0.1, 0.4)
        elif x >= 800:
            x = 800; self.vx = -abs(self.vx) - random.uniform(0.1, 0.4)
        if y <= 0:
            y = 0; self.vy = abs(self.vy) + random.uniform(0.1, 0.4)
        elif y >= 600:
            y = 600; self.vy = -abs(self.vy) - random.uniform(0.1, 0.4)

        self.rect.center = (x, y)
         

class Roast(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("roast.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.speed = 4

    def update(self):
        x, y = self.rect.center
        y += self.speed
        self.rect.center = (x, y)
        # if roast falls off screen, remove it
        if y > 600:
            self.kill()


if __name__ == "__main__":
    main = Main()
    main.main()