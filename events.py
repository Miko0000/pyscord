import pyska
import discord
import commands
from config import token
from logging import Handler
from threading import Thread

class PyscordClient(discord.Client):
	handler = {
		"ready": None,
		"message": None
	}

	iface = None

	async def on_ready(self):
		handler = self.handler["ready"]
		if handler is not None:
			handler(self)

	async def on_message(self, message):
		#handler = self.handler["message"]
		#if handler is not None:
		#	handler(self, message)
		iface = self.iface
		iface.invoke("f.highlight")
		iface("[%s] " % message.author.username)
		iface.invoke("f.normal")
		iface("%s\n" % message.content)

intents = discord.Intents.default()
intents.message_content = True

client = PyscordClient(intents=intents)

pyscord_thread_stop = 0
def pyscord_thread():
	client.run(token, log_handler=None)

	while pyscord_thread_stop <= 0:
		pass

	client.stop()
	quit(0)

def input(entity, iface):
	ifin = iface.get("input")
	ifout = iface.get("output")

	ifout.request()
	ifout.invoke("f.normal")
	ifout("")
	input = ifin();
	if input == ";exit":
		return 1

	ifout.release()

	#print("! %i\n", ifout.state)
	#ifout("> %s\n" % input)

	commands.run(client, iface, input)

	return 0

def init(entity, iface):
	global now
	output = iface.get("output")

	def on_ready(client):
		output.invoke("f.normal")
		output("Logged in!\n")

	client.handler["ready"] = on_ready

	def on_message(client, message):
		print('[', message.author.username, message.content, ']', flush=True)

		"""
		output = iface.get("output")
		output.options["incoming"] = 555123213

		output.invoke("f.highlight")
		output("[%s] " % message.author.username)
		#output.buffer = "[%s]" % message.author.username

		output.invoke("f.normal")
		output("%s\n" % message.content)
		#output.buffer = "%s\n" % message.content
		"""

	client.handler["message"] = on_message
	client.iface = iface;
	now = input

	return 0

now = init
thread = Thread(None, pyscord_thread)
thread.start()
