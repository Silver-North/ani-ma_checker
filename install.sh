#! /bin/bash


file_text='{ "mode": "lightmode", "about": " Checking sites\n Anime:\n> https://animevost.org\n Manga:\n> https://mintmanga.live\n> https://readmanga.io\n> https://manga-chan.me\n Ranobe:\n> https:ранобэ.рф\n> https://tl.rulate.ru\n> https://ranobehub.org\n> https://ruranobe.ru", "geometry": [ 480, 55, 400, 300 ], "anime": { "urls": [], "series": [], "ova": [], "name": [], "log": "", "description": [], "images": [], "track-name": [], "track-link": [] }, "manga": { "urls": [], "numbers": [], "change_numbers": [], "names": [], "logs": [], "images": [], "description": [] }, "ranobe": { "urls": [], "names": [], "chapters": [], "access-chapters": [], "future-chapters": [], "description": [], "images": [], "log": "" }, "notify": { "notify": "empty", "anime": [], "manga": [], "ranobe": [] }, "history": { "anime": [], "manga": [], "ranobe": [] } }'
list_file=$(ls | grep setting.json | grep -v grep)


if [[ $list_file != "settings.json" ]]; then
	pip3 install -r requirements.txt;
	echo $file_text > setting.json;
fi
