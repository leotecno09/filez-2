var phrases = ["Do not use FilEZ as your main cloud file manager!", "Visual Studio Code is the best editor.", "Yes.. this is open source", "this is like splashes.txt of Minecraft", "All your files has been encrypted.", "Go to /static/scripts/JS/random_footer_text.js to see the javascript that randomizes this phrases!", "HI!", "Una frase in italiano perchè si...", "Error in line 5 of random_footer_text.js", "Do you remember FilEZ v1.0?", "", "https://magik.lorismagik.net", "https://github.com/leotecno09/filez-2/tree/master"]

const randomTextDiv = document.getElementById("randomText");

var randomPhraseIndex = Math.floor(Math.random() * phrases.length);
var randomPhrase = phrases[randomPhraseIndex];

randomTextDiv.textContent = randomPhrase;