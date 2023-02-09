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
        
    def __call__(self, facing):
        return self.frames[facing][self.frame_index]
        
def add_rev_anim(frames:list):
    frames.extend(frames[-2::-1])
    return frames

move_right_key = pygame.K_d
move_left_key = pygame.K_a
jump_key = pygame.K_SPACE
class Goril:
    def __init__(self, screen):
        self.x, self.y = 0, 0    # Bottom x, y
        self.x_max, self.y_max = screen.get_size()
        self.x_vel, self.y_vel = 0, 0
        
        self.walk_vel = 0.25
        self.jump_vel = 2
        self.gravity = 0.005
        self.facing = 'right'
        self.status = 'idle'
        self.is_on_floor = False
                
        self.walk_anim = Animashyun([pygame.image.load(f"monke\\walk\\Monke Walk {i}.png") for i in range(1, 9)], 125)
        self.jump_anim = Animashyun(add_rev_anim([pygame.image.load(f"monke\\jump\\Monke jump {i}.png") for i in range(1, 6)]), (2*self.jump_vel/self.gravity)/9-2.5)
        
    def update(self, dt, floor=800):
        self.x += self.x_vel*dt
        
        if self.y >= floor and self.y_vel > 0: self.on_floor()
            
        else: self.y_vel = self.y_vel+self.gravity*dt 
        self.y = min(floor, self.y+self.y_vel*dt)
        
        match self.status:
            case 'walk':
                self.walk_anim.tick(dt)
                if self.facing == 'left': 
                    self.x = max(self.x-self.walk_vel*dt, 0)
                else: 
                    self.x = min(self.x+self.walk_vel*dt, self.x_max)
                
            case 'jump':
                self.jump_anim.tick(dt)
    
    def draw(self, screen):
        match self.status:
            case 'walk' | 'idle':
                self.walk_anim.rect.midbottom = self.x, self.y
                screen.blit(self.walk_anim(self.facing), self.walk_anim.rect)
            
            case 'jump':
                if not self.is_on_floor:
                    self.jump_anim.rect.midbottom = self.x, self.y
                    screen.blit(self.jump_anim(self.facing), self.jump_anim.rect)
                    
                    if self.keys[move_right_key] or self.keys[move_left_key]:
                        self.facing = 'right' if keys[move_right_key] else 'left'
                        if self.facing == 'left': 
                            self.x = max(self.x-self.walk_vel*dt, 0)
                        else: 
                            self.x = min(self.x+self.walk_vel*dt, self.x_max)
    
    def on_floor(self):
        self.y_vel = 0
        self.is_on_floor = True
        if self.status == 'jump':
            self.status = 'idle'
    
    def jump(self):
        if self.is_on_floor:
            self.y_vel -= self.jump_vel
            self.status = 'jump'
            self.is_on_floor = False
    
    def keys_pressed(self, keys):
        self.keys = keys
        if keys[jump_key]: self.jump()
        
        elif (keys[move_right_key] or keys[move_left_key]) and self.is_on_floor: 
            self.status = 'walk' if keys[move_right_key] ^ keys[move_left_key] else 'idle'
            self.facing = 'right' if keys[move_right_key] else 'left'
        else: 
            if self.is_on_floor: self.status = 'idle'
        
        
    
if __name__ == '__main__':
    FPS = 60
    screen = pygame.display.set_mode((1000, 850))
    clock = pygame.time.Clock()
    
    goril = Goril(screen)
    run = True
    while run:
        dt = clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                   
        keys = pygame.key.get_pressed()
        
        goril.keys_pressed(keys)
        screen.fill((30, 30, 30))
        goril.update(dt if dt != 0 else 1/FPS)
        goril.draw(screen)
        
        
        pygame.display.update()

    
    pygame.quit()