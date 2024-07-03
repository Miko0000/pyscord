import asyncio
import config
import time

def input_parse(input):
	return filter(bool, input.split(' '))

guild = None
channel = None
client = None
def command_status(client, iface, input):
	output = iface.get("output")
	output("[ %s ]\n" % config.status)

def command_guilds(client, iface, input):
	output = iface.get("output")

	i = 0
	while i < len(client.guilds):
		output.invoke("f.options", i)
		output("%s\n" % client.guilds[i])

		i += 1

	output.invoke("f.normal")

def command_guilds_select(client, iface, input):
	global guild

	output = iface.get("output")
	args = list(input_parse(input))

	if len(args) <= 0:
		output.invoke("f.error")
		output("Insufficient arguments")

		output.invoke("f.normal")
		output("\n")

		return

	sel = -1

	try:
		sel = int(args[1])

	except:
		pass

	if sel < 0:
		output.invoke("f.error")
		output("Invalid input: %s" % args[1])

		output.invoke("f.normal")
		output("\n")

		return

	try:
		guild = client.guilds[sel]
	except:
		output.invoke("f.error")
		output("Failed to select guild")

		output.invoke("f.normal")
		output("\n")

		return

	output.invoke("f.highlight")
	output("Selected %s\n" % guild.name)
	output.invoke("f.normal")

def command_channels(client, iface, input):
	output = iface.get("output")

	i = 0
	while i < len(guild.channels):
		output.invoke("f.options", i)
		output("#%s\n" % guild.channels[i])

		i += 1

	output.invoke("f.normal")

	return

def command_channels_select(client, iface, input):
	global channel

	output = iface.get("output")
	args = list(input_parse(input))

	if len(args) <= 0:
		output.invoke("f.error")
		output("Insufficient arguments")

		output.invoke("f.normal")
		output("\n")

		return

	sel = -1

	try:
		sel = int(args[1])

	except:
		pass

	if sel < 0:
		output.invoke("f.error")
		output("Invalid input: %s" % args[1])

		output.invoke("f.normal")
		output("\n")

		return

	try:
		channel = guild.channels[sel]
	except:
		output.invoke("f.error")
		output("Failed to select channel")

		output.invoke("f.normal")
		output("\n")

		return

	output.invoke("f.highlight")
	output("Selected %s\n" % channel.name)
	output.invoke("f.normal")

def command_chat(client, iface, input):
	ifin = iface.get("input")
	ifout = iface.get("output")

	ifin.options["prefix"] = "\u2709 "
	while True:
		ifout.request()
		ifout.invoke("f.normal")
		ifout("")
		input = ifin();
		if input in ("\033", '.'):
			ifout.release()

			break

		loop = client.loop
		task = asyncio.run_coroutine_threadsafe(
			channel.send(content=input), loop
		)

		ifout.release()

	ifin.options["prefix"] = "> "

def command_clear(client, iface, input):
	iface.get("output").invoke("clear")

def command_debug(client, iface, input):
	output = iface.get("output")
	input = iface.get("input")
	output.invoke("f.normal")
	output("[output.requests] %i\n" % output.request_count)
	# output("[output.options] %i\n" % output.options["incoming"])
	output("[output.length] %i\n" % len(output.buffer[0]))
	output("[input.requests] %i\n" % input.request_count)

commands = {
	";s": command_status,

	";g.s": command_guilds_select,
	";g": command_guilds,

	";clr": command_clear,
	";c.s": command_channels_select,
	";c": command_channels,
	".": command_chat,
	"/": command_debug
}

def run(client, iface, input):
	for command in commands:
		if input.startswith(command):
			commands[command](client, iface, input)

			return
