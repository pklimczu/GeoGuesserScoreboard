from gmail import GmailService
from datetime import date
import os

today = date.today()
title = "Backup {}".format(today)

path = os.getcwd() + "/../../instance/"
gs = GmailService()
recipent_mail = ""
gs.send_mail_with_attachment(recipent_mail, title, "Geoguesser Scoreboard", path, "app.sqlite")