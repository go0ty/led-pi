import sys
import argparse
import colorsys
import math
import time

def parse_args(args):
	# Getting command line arguments
	parser = argparse.ArgumentParser(description="LED Strip Controller")
	parser.add_argument("--leds", type=int, help="The number of LEDs in the strip")
	parser.add_argument("--interval", type=float, help="The interval time in milliseconds between each packet")
	parser.add_argument("--console-debug", action="store_true", help="Output packets to console, ignore LED")
	return parser.parse_args(args)

def main_loop(args):
	frequency = 0.5
	phase = 0
	baseHue = 0

	print "Beginning Main Loop"
	while True:
		# Loop through each LED and assign a color
		leds = []
		for x in range(args.leds):
			# Evaluate for each LED
			hue = math.sin(x*frequency+phase)+baseHue
			leds.append(hue)

		# Update LED Colors
		if (args.console_debug):
			print leds
		else:
			# Send Packet
			pass

		# Update the Values
		baseHue += 1
		if baseHue > 359:
			baseHue = 0
		phase += 0.5
		if phase > 100:
			phase = 0
		frequency += 0.05
		if frequency > 2:
			frequency = 0.5

		# Wait until next interval
		time.sleep(args.interval)


if __name__ == "__main__":
	# Parse Arguments
	parsed_args = parse_args(sys.argv[1:])
	# Begin main LED Loop
	main_loop(parsed_args)
