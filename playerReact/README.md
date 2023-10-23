# Steps to create a new version of the Videoheadline playerReact:
1. Make the changes and compile using npm run build.
2. Copy the compiled CSS and JS to player/static/player/css and player/static/player/js, respectively.
3. Delete the old CSS and JS files in player/static/player/css and player/static/player/js.
4. In the player/templates/player/index.html template, change the names of the CSS and JS files to which the template points.
5. Test in Videoheadline to ensure that the player is working correctly.
# Important Notes:
When modifying the player, ensure that it continues working in IE 11 on Windows 10 and 8.1. It doesn´t work on Windows 7 with IE 11.