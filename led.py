import sys
import argparse
import math
import time
import colorsys
import random
from dotstar import Adafruit_DotStar

def parse_args(args):
	# Getting command line arguments
	parser = argparse.ArgumentParser(description="LED Strip Controller")
	parser.add_argument("--numPixels", type=int, help="The number of LEDs in the strip")
	parser.add_argument("--interval", type=float, help="The interval time in milliseconds between each packet")
	parser.add_argument("--sparkles", action="store_true", help="Add intermittent white sparkles along the LED Strip")
	parser.add_argument("--detachedStrip", action="store_true", help="Output packets to console, ignore LED")
	return parser.parse_args(args)

def init_led(numPixels):
	strip = Adafruit_DotStar(numPixels, 12000000)
	strip.begin()
	strip.setBrightness(32)
	return strip

def main_loop(args):
	# DotStar Interface
	if not args.detachedStrip:
		strip = init_led(args.numPixels)

	# Timing Parameters
	frequency = 0.05
	phase = 0
	baseHue = 0
	sparkle = None

	print "Beginning Main Loop"
	while True:
		# Loop through each LED and assign a color
		leds = []
		for x in range(args.numPixels):
			# Evaluate for each LED
			hue = 25*math.sin(x*frequency+phase)+baseHue
			rgb = colorsys.hls_to_rgb(hue/360, 0.5, 1)
			hex = '%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
			leds.append(hex)

		# Overwrite with Sparkles, if defined
		if args.sparkles:
			if sparkle is None and random.randint(1,100) < 2:
				# Small Chance to spawn a new Sparkle somewhere along the Strip
				sparkle = ((random.randint(0,args.numPixels-2),0))
			if sparkle is not None:
				# Render Sparkle and push along the path
				leds[sparkle[0]] = 'FFFFFF'
				sparkle = (sparkle[0] + 2, sparkle[1] + 1)

				if sparkle[1] > 10 or sparkle[0] > args.numPixels -2:
					sparkle = None # Delete is lifetime is up, or path end is reached

		# Update LED Colors
		if (args.detachedStrip):
			print leds
		else:
			# Send Packet
			for x in range(len(leds)):
				strip.setPixelColor(x,int(leds[x], 16))
			strip.show()

		# Update the Values
		baseHue += 0.2
		if baseHue == 360:
			baseHue = 0
		phase += 0.01
		if phase == 100:
			phase = 0

		# Wait until next interval
		time.sleep(args.interval)


if __name__ == "__main__":
	# Parse Arguments
	parsed_args = parse_args(sys.argv[1:])
	# Begin main LED Loop
	main_loop(parsed_args)
