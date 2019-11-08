from gmail import GmailService
from datetime import date
import os

today = date.today()
title = "Backup {}".format(today)

path = os.getcwd() + "/../../instance/"
gs = GmailService()
gs.send_mail_with_attachment("quczmil@gmail.com",title,"Geoguesser Scoreboard",path,"app.sqlite")