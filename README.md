About this:
===========

This is a fork of ISO-B's pmb-pitft project with a few additions. This was running on a RPi 2 with an Adafruit 3.5" TFT resistive screen and Volumio 1.55.

![pmb-pitft](https://volumio.org/forum/resources/modified-pmb-pitft-touch-interface-control-mpd/1168)

Additions:
==========

- support for 3.5" TFT screens with 480x320px
- additional screen for library file browsing - page-by-page touch swipe through library folders, folders/tracks can be added to playlist
- additional screen for playlist browsing - delete tracks/whole playlist
- additional screen for MPD settings (repeat/consume/refresh etc)
- touch "timeline" to jump to that time in the track
- cover art 'cover.jpg' taken from folder of current song
- sample rate / filetype displayed
- IRKey remote - playback control and playlist/library browse functions accessed from Adafruit IRKey remote(USB k/board)


Installing:
===========

Use Adafruit install procedure to get your 3.5" screen working and then skip to the part of the instructions below at the point where pygame is installed. (starts at "After that editing and creating files its time to give some commands to pi.")

then:
 - download the following fonts from FontSquirrel, Bebas-Neue Regular and Bebas-Neue Bold. Create a new folder called "BebasNeue-TTF". Copy the two fonts into this new folder.
 


Notes:
======

The screen layout is arranged for a screen that has been rotated 270 degs.

To go to the library list, touch the album artwork on the main screen (or touch where the artwork will display)
   - swipe up or down to go through the folders in your library. touch the scrollbar to go to that point in the library.
   - touch the folder name to go into a folder, touch the "folder back" icon (bottom right) to go back up the folder hierarchy
   - to add a folder to the playlist, touch the "plus folder" icon on the left next to the folder. To add a track, touch the "music plus" icon to the left of the track

To go to the playlist, touch the track name
   - touch the "x" to the left of the track to delete it from the playlist. Touch the garbage can to remove all tracks
   -  From the playlist screen, touch the "gears" icon to go to the settings screen. Each icon is a toggle, that has blue text when enabled.
   
   
To Do:
======

 - smooth scrolling through the library & playlist when swiping (rather than a page-by-page scrolling)
 - Swiping (with the screen 'sliding' to display the new screen) on the mainscreen to go to the library/playlist and settings screens. ie. swipe left to go to the playlist, swipe right to go to the music library list
 - list library by artwork rather than showing folders
 - clean up the code, utilizing proper OOP techniques.


PMB-PiTFT (Pi MusicBox PiTFT) is small Python program/script/whatever that uses mopidy's mpd-api to show controlling ui on Raspberry Pi's screen.

Features:
===========
Shows following details of currently playing track:
- Cover art (From Last.FM)
- Artist, Album and Track title
- Track time total and elapsed

Shows and let user control:
- Repeat
- Random
- Volume
- Playback status

Let user control:
- Screen backlight

Also haves sleep function to turn screen of and stop music after certain time.

Things you need:
=================
- Raspberry pi (I am using model B rev.1)
- Adafruit PiTFT with Resistive Touchscreen ( http://www.adafruit.com/product/1601 )(Bought mine from ModMyPi: https://www.modmypi.com/pi-tft-raspberry-pi-touchscreen )
- Internet connection for Pi
- [Optional] PiBow TFT Raspberry Pi Case ( http://shop.pimoroni.com/products/pitft-pibow ) (Bought mine from ModMyPi: https://www.modmypi.com/pimoroni-pitft-case )
- [Optional] Helvetica Neue Bold-font. You can use normal Helvetica Bold as well or some other font.

Known issues:
==============
- PiTFT touchscreen is not working with Pi2, yet.
- Capacitive PiTFT does not work with Pi1 B rev1. (Model B rev 1 have an older layout for the I2C pins and won't be able to use the touch screen.)

Installing:
===========
Current installing guide is tested and working with: Resistive PiTFT + Raspberry Pi 1 Model B rev1 + Pi MusicBox v.0.53 . Resistive PiTFT should work fine with all Pi1 B models. I haven't had time and equipment to test capacitive PiTFT yet, but it should work also, except that you need to do small changes to make backlight work (https://github.com/ISO-B/pmb-pitft/issues/1). 

First you need to install and configure Pi MusicBox(PMB). Instructions and everything else you need for this can be found on their website http://www.pimusicbox.com/ 
Make sure you enable ssh and set root password.

After installing and configuring PMB its time to take ssh connection to you PMB using ssh and root account. Use your favorite ssh program. I am using putty.
After logging in enter following commands:
<pre>
apt-get install rpi-update
echo insecure >> ~/.curlrc
REPO_URI=https://github.com/notro/rpi-firmware rpi-update 4815829b3f98e1b9c2648d9643dfe993054923ce
reboot
</pre>

Wait until your PMB is booted and log back in using ssh. Next you will need your favorite file-editor on pi. I use nano.

<pre>Open file: /etc/modprobe.d/raspi-blacklist.conf
Change line: blacklist spi-bcm2708
	 To: #blacklist spi-bcm2708
and save the file</pre>

<pre>Open file: /etc/modules
add following lines end of file and save it.
spi-bcm2708
fbtft_device
stmpe_device
gpio_backlight_device</pre>

<pre>Make file: /etc/modprobe.d/pitft.conf
add following lines to that file and save it.
options fbtft_device name=pitft rotate=270 frequency=32000000
options stmpe_device cs=1 chip=stmpe610 blocks=gpio,ts irq-pullup irq-gpio=24 irq-base=330 sample-time=4 mod-12b=1 ref-sel=0 adc-freq=2 ave-ctrl=3 touch-det-delay=4 settling=2 fraction-z=7 i-drive=0
options gpio_backlight_device gpio=252</pre>

After that editing and creating files its time to give some commands to pi.
<pre>apt-get update
apt-get install fbi
apt-get install python-pygame
pip install python-mpd2
apt-get install evtest tslib libts-bin</pre>

We need to make symlink for touchscreen.
<pre>Open file: /etc/udev/rules.d/95-stmpe.rules
and add following line there and save it.
SUBSYSTEM=="input", ATTRS{name}=="stmpe-ts", ENV{DEVNAME}=="*event*", SYMLINK+="input/touchscreen" </pre>

Time to reboot pi one more time. Give command: <code>reboot</code>

Once pi is booted again log back in.
Lets verify that your screen is working.
Enter following commands and you should see image on your pi's screen. If so everything is ok.
<pre>wget http://adafruit-download.s3.amazonaws.com/adapiluv320x240.jpg
fbi -T 2 -d /dev/fb1 -noverbose -a adapiluv320x240.jpg</pre>

Calibrate touch screen using adafruits tutorial: https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/touchscreen-install-and-calibrate#manual-calibration

Download pmb-pitft files from github.
To be sure to start in the home directory do

<code>cd ~</code>

Then download the following for cloning the git:

<code>apt-get install git-core</code>

After installing clone the git:

<code>git clone https://github.com/ISO-B/pmb-pitft.git</code>

From pitft-ui.py you need to change font if you are using something else than Helvetica Neue Bold and check that path is correct.

To change font edit /root/pmb-pitft/pmb-pitft/pitft_ui.py file line 26 and replace "helvetica-neue-bold.ttf" with your own font name. example "OpenSans-Bold.ttf". You can download Open Sans from www.fontsquirrel.com/fonts/open-sans. Transfer ttf file to /root/pmb-pitft/pmb-pitft/ folder.

This is now daemon and it has three commands: start, restart and stop
Use following command to start ui:

<code>sudo python /root/pmb-pitft/pmb-pitft/ui.py start</code>



TO-DO:
=========
- Easy option to switch between capasitive and resistive PiTFTs
- Gestures
- Playlist selector
- Got other ideas? Post issue and tell me about it

Author notes:
=============
There is probably better way doing somethings that I have done. It would have been awesome to have this as mopidy extension, but I couldn't find way to pull that out. Since pygame screen things need root account/access. This took lot of trial and error. I have installed pi musicbox again and again counteless time before I managed to audio work with screen.

There might be some bugs left, but don't worry we can fix those, hopefully. Feel free to give any improvement ideas.

Thanks:
===========
<pre>Pi MusicBox Team
For making this great audio system
http://www.pimusicbox.com/</pre>

<pre>Notro and other people on project FBTFT
For making drivers for screen
https://github.com/notro/fbtft/wiki</pre>

<pre>project pylast @ github
For their Last.FM Python library
https://github.com/pylast/pylast</pre>

<pre>project python-mpd2 @ github
For their MPD-client Python library
https://github.com/Mic92/python-mpd2</pre>

<pre>Matt Gentile @ Icon Deposit
For his awesome Black UI Kit
http://www.icondeposit.com/design:108</pre>

<pre>Biga
Petite Icons
http://www.designfreebies.com/2011/10/20/petite-icons/</pre>
