NOTE: The script assumes the radio is a Wouxun KG-805g.

Download and install chirp wheel using `pipx`:
```
wget https://archive.chirpmyradio.com/chirp_next/next-20250502/chirp-20250502-py3-none-any.whl
pipx install ./chirp-20250502-py3-none-any.whl
```

Get an updated image from the CERT radio guys and run the `create_jtp_image` script on it:
```
./create_jtp_image 'KG805g CERT v2.img'
```

Upload the image to the radio using the following command:
```
chirpc -s /dev/ttyUSB0 -r Wouxun_KG-805G --upload-mmap --mmap 'KG805g CERT v2 plus JTP.img'
```
