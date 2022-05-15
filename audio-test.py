import pygame, numpy, pygame.sndarray

sampleRate = 44100
# 44.1kHz, 16-bit signed, mono
pygame.mixer.pre_init(sampleRate, -16, 1)
pygame.init()
surface = pygame.display.set_mode((400, 300))
arr = numpy.array(
    [
        4096 * numpy.sin(2.0 * numpy.pi * 440 * x / sampleRate)
        for x in range(0, sampleRate)
    ]
).astype(numpy.int16)
sound = pygame.sndarray.make_sound(arr)

while True:
    color = (255, 255, 255)
    surface.fill(color)
    pygame.display.flip()

    sound.play(-1)
    pygame.time.delay(500)
    sound.stop()

    color = (0, 0, 0)
    surface.fill(color)
    pygame.display.flip()
    pygame.time.delay(500)
