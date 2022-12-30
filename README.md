# Boris' Movie Database (BMDb) - a web app for movie suggestion

youtube video of the project :  https://www.youtube.com/watch?v=BcuG5aSp-NA&ab_channel=Bobox948

#### Description:

My project is a web application, written in python using the flask framework, SQL (database), HTML/CSS and a little bit of javascript. This project took me 9 days of almost all day working on it, several hours a day (like maybe 3 hard psets worth of work).

The web application is called "Boris' movie database (BMDb)" which is a web app for movie suggestions. The data is indirectly from IMDB, via Maancham (github) which offers a csv file with movies, their description, rating, year, director, actors etc directly in that all in one file. And the IMDB Api not seems to be free, so I took this CSV files, cleaned it a little bit, added an unique ID to each movie, deleted a few fields that weren't interesting for my project and let's go! I imported this file into sqlite3 and created 4 tables, "movies", which contains all of the informations that I listed before, "users", which contains the informations about users like login and hashed password, including also the year of birth, "seen", which contains the user id and the movie id of the movies that the user has already seen and that won't be suggested again, and finally "reviews" containing the user id, the movie id and a review text field, to store the users reviews of each movie. Those two tables "seen" and "reviews" can communicate with the "movies" and "users" tables via "movie_id" and "users_id". The "layout.html" file contains the structure of the different htmls.

First, we arrive on the login.html page where you can login into the webapp. I've chosen for the style of the website to have all the background in black, and the texts either in yellow or white, that way it ressembles to the cinema environnement. I made those styles in the styles.css file.
So to login, it's classic, you have to provide a username and a password. If the username or the password is incorrect, an error is shown on a new page called apology.html, whick shows the grumpy cat with an error message like in pset9 finance (I love this cat).

You can of course register, via register.html, where you are asked for an username, a password, a password confirmation and the year of your birth. The year of your birth if asked because we will filter the suggestions for your movies with a range of 10 years before your birth to 20 years after it, so that a person which was born in 1991 won't get movies before 1981 and after 2021, because otherwise I think the person won't like it (too oldschool or too "recent").

After your registration, you come back on login page and you can login. I made sure that when you are logged in, if you go to "/login.html" or "/register.html" via the url, you are redirected to "/" (or you stay in "/") with an error message via flash saying that you are already logged in or registered. I made that in the app.py file.

So after the login, you are redirected to "/" or index.html. Here, you have checkboxes for movie categories (comedy, drama, etc...). You are asked, according to your mood of the day, to choose at least one category (if not, "apology" page is loaded) and a maximum of 3, and then you have a submit button to get your movie suggestion/recommendation (these informations are written in the page so the user knows them). If you don't chose at least one category, you are redirected to "apology.html" with the grumpy cat and if you want to choose more than 3, the javascript script doesn't allow it.

After your choice, you are redirected to "/suggestion.html" and here you have the title and the description, in a table, of the 5 highest ranked movies in the database according to the genres of the movies that you've chosen and according to the year range mentioned above. This result (how the ranking suggestion system works) is explained to the user with a paragraph in the html. Then under the table, you have "two forms in one" with one submit button. First, in the left, you have checkboxes, to tell the server and the database if you have already seen some of the movies suggested, in order not to get them suggested again, and in the right a select dropdown menu to choose the movie that you wan't to watch today (this is explained in the page for the user of course).
Of course, if you have seen all the movies already, you can check all the 5 checkboxes, and you leave the dropdown menu empty. If you choose less than 5 movies in the checkbox, you have to choose the last in the dropdown menu, if not you will get an error, and a redirection to "apology.html" with a special message. If you chose 5 movies in the checkboxes, you will also be redirected to "/apology" but the message will say to go back to homepage and create the filters again, and those 5 movies won't be suggested again.
If you chose the same movie in the checkbox and in the dropdown menu, you get an error redirection to apology saying that "you told us that you have already seen this movie!".
You also have a footer at the page to tell the user where the data came from.
Note that if your combination of choices doesn't lead to at least one movie (like the combination of comedy, sport, and history), you get redirected to "empty.html" telling you that there is no match for your choices, and you are proposed to click on homepage via href to go back to submit other choices. That happens because the 3 categories chosen have to be in the list of the genres of the movies, via SQL select request (AND, not OR).

After you submit your choices, you arrive at "enjoy.html", and a message tells you to enjoy your movie with some popcorns and the background image of the page, is a theater room. You can now go back to homepage after your movie if you have left this page open or, if you closed it, when you come back after your movie to the website, in the homepage, you have a widget "my movies & write a review" which redirects to "seen.html".
In there, you can see an unordered list (but ordered alphabetically) of all the movies that you've seen. You then can choose in a select dropdown menu the movie you want to write a review about, and you have a textarea and an input button to submit your review. Once it's done, you are redirected to "review.html" that tells you that your review was submitted. Once you wrote a review, of course, you can't submit another again on that movie, because it disappears from the list to review.

Then, you have another widget called "my reviews" which redirects to "reviews.html" and there, you can see all your reviews, which the title of the movie and the review, ordered alphabetically but in htlm tags of unordered list!

and VOILA!

This was 50. The best introduction course to CS ever. Props to David Malan and the other teachers.











