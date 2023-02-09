import pygame

class Animashyun:
    def __init__(self, frames, frame_duration, generate_mirrored_frames=True, facing='right'):
        """
        frame_duration: in milliseconds
        """
        
        frames = self.process_frames(frames)
        self.num_frames = len(frames)
        self.rect = frames[0].get_rect()
        self.frame_duration = frame_duration    
        self.frame_index = 0
        self.t = 0
        self.next_frame_at = self.t + self.frame_duration
        
        self.frames = {}
        self.frames[facing] = frames
        self.frames['left' if facing == 'right' else 'right'] = [pygame.transform.flip(frame, 1, 0) for frame in frames]
    
    def process_frames(self, frames, mode='bottom'):
        frame_dimens = [f.get_size() for f in frames]
        
        # Check if frames are of same dimensions
        for f in frame_dimens:
            if f != frame_dimens[0]: break
        else: return
        
        x_max, y_max = max(frame_dimens, key=lambda x: x[0])[0], max(frame_dimens, key=lambda x: x[1])[1]
        centered_frames = []
        
        if mode == 'bottom':
            for frame in frames:
                surf = pygame.Surface((x_max, y_max), pygame.SRCALPHA)
                rect = frame.get_rect()
                rect.midbottom = x_max//2, y_max
                surf.blit(frame, rect)
                centered_frames.append(surf)
        
        return centered_frames
    
    def tick(self, dt):
        self.t += dt
        if self.t >= self.next_frame_at:
            self.next_frame_at += self.frame_duration
            self.frame_index = (self.frame_index+1) % self.num_frames
    
    def reset(self):
        self.frame_index = 0
        self.t = 0
        self.next_frame_at = self.t + self.frame_duration
        
    def __call__(self, facing):
        return self.frames[facing][self.frame_index]

class CrouchAnimashyun(Animashyun):
    def __init__(self, frames, frame_duration, generate_mirrored_frames=True, facing='right'):
        super().__init__(frames, frame_duration, generate_mirrored_frames, facing)
        self.ground_pound_sprite = pygame.image.load("monke\\crouch\\Monke Ground Pound.png")
        self.is_ground_pounding = False
        
    def tick(self, dt):
        self.t += dt
        if self.t >= self.next_frame_at:
            self.next_frame_at += self.frame_duration
            self.frame_index = min((self.frame_index+1), self.num_frames-1)
        
    def untick(self, dt):
        self.t += dt
        if self.t >= self.next_frame_at:
            self.next_frame_at += self.frame_duration
            self.frame_index = max((self.frame_index-1), 0)
            return
        if self.frame_index == 0: 
            return True
    
    def __call__(self, facing):
        return self.frames[facing][self.frame_index] if not self.is_ground_pounding else self.ground_pound_sprite
    
def add_rev_anim(frames:list, repeat_last = False):
    if not repeat_last: frames.extend(frames[-2::-1])
    else: frames.extend(frames[-1::-1])
    return frames

move_right_key = pygame.K_d
move_left_key = pygame.K_a
jump_key = pygame.K_SPACE
crouch_key = pygame.K_s

class Goril:
    def __init__(self, screen):
        self.x, self.y = 0, 0    # Bottom x, y
        self.x_max, self.y_max = screen.get_size()
        self.x_vel, self.y_vel = 0, 0
        
        self.walk_vel = 0.25
        self.jump_vel = 2
        self.gravity = 0.005
        self.ground_pound_gravity_factor = 3
        self.facing = 'right'
        self.state = 'idle'
        self.is_on_floor = False
        self.is_crouch = False
                
        self.walk_anim = Animashyun([pygame.image.load(f"monke\\walk\\Monke Walk {i}.png") for i in range(1, 9)], 120)
        self.jump_anim = Animashyun(add_rev_anim([pygame.image.load(f"monke\\jump\\Monke jump {i}.png") for i in range(1, 6)], repeat_last=True), (2*self.jump_vel/self.gravity)/10)
        self.crouch_anim = CrouchAnimashyun([pygame.image.load(f"monke\\crouch\\Monke crouch {i}.png") for i in range(1, 4)], 120)
        
        
    def update(self, dt, keys, floor=800):
        self.keys_pressed(keys)
        self.x += self.x_vel*dt
        
        if self.y >= floor and self.y_vel > 0: self.on_floor()
            
        else: 
            if not self.crouch_anim.is_ground_pounding: self.y_vel = self.y_vel+self.gravity*dt 
            else: self.y_vel = self.y_vel+self.gravity*self.ground_pound_gravity_factor*dt 
        self.y = min(floor, self.y+self.y_vel*dt)
        
        match self.state:
            case 'walk':
                self.walk_anim.tick(dt)
                if self.facing == 'left': 
                    self.x = max(self.x-self.walk_vel*dt, 0)
                else: 
                    self.x = min(self.x+self.walk_vel*dt, self.x_max)
                
            case 'jump':
                self.jump_anim.tick(dt)
                if self.keys[move_right_key] or self.keys[move_left_key]:
                        self.facing = 'right' if self.keys[move_right_key] else 'left'
                        if self.facing == 'left': 
                            self.x = max(self.x-self.walk_vel*dt, 0)
                        else: 
                            self.x = min(self.x+self.walk_vel*dt, self.x_max)
            
            case 'crouch':
                self.crouch_anim.tick(dt)
            case 'uncrouching':
                if not self.crouch_anim.untick(dt):
                    self.state = 'idle'
    
    def draw(self, screen):
        match self.state:
            case 'walk' | 'idle':
                self.walk_anim.rect.midbottom = self.x, self.y
                screen.blit(self.walk_anim(self.facing), self.walk_anim.rect)
            
            case 'jump':
                if not self.is_on_floor:
                    self.jump_anim.rect.midbottom = self.x, self.y
                    screen.blit(self.jump_anim(self.facing), self.jump_anim.rect)
                    
            case 'crouch' | 'uncrouching':
                self.crouch_anim.rect.midbottom = self.x, self.y
                screen.blit(self.crouch_anim(self.facing), self.crouch_anim.rect)
            
    
    def on_floor(self):
        self.y_vel = 0
        self.is_on_floor = True
        if self.state == 'ground pounding':
            self.state = 'uncrouching'
        if self.state == 'jump':
            self.walk_anim.reset()
            self.state = 'idle' # if not self.crouch_anim.is_ground_pounding else 'uncrouching'
            self.jump_anim.reset()
    
    def jump(self):
        if self.is_on_floor:
            self.y_vel -= self.jump_vel
            self.state = 'jump'
            self.is_on_floor = False
    
    def crouch(self):
        if self.is_on_floor:
            self.is_crouch = True
            self.state = 'crouch'
        
        elif self.state == 'jump':
            self.crouch_anim.is_ground_pounding = True
            
            
    
    def keys_pressed(self, keys):
        self.keys = keys
        if keys[jump_key]: self.jump()
        elif keys[crouch_key]: self.crouch()
        elif (keys[move_right_key] or keys[move_left_key]) and self.is_on_floor: 
            self.state = 'walk' if keys[move_right_key] ^ keys[move_left_key] else 'idle'
            self.facing = 'right' if keys[move_right_key] else 'left'
        else: 
            if self.is_crouch:
                self.crouch_anim.reset()
                self.state = 'uncrouching'
                self.is_crouch = False
            if self.is_on_floor and self.state != 'uncrouching': 
                if not self.crouch_anim.is_ground_pounding:
                    self.state = 'idle'
                else:
                    self.crouch_anim.is_ground_pounding = False
                    self.state = 'uncrouching'
                
        
if __name__ == '__main__':
    FPS = 144
    screen = pygame.display.set_mode((1000, 850))
    clock = pygame.time.Clock()
    
    goril = Goril(screen)
    run = True
    while run:
        dt = clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        screen.fill((30, 30, 30))
        goril.update(dt if dt != 0 else 1/FPS, pygame.key.get_pressed())
        goril.draw(screen)
        
        
        pygame.display.update()

    
    pygame.quit()