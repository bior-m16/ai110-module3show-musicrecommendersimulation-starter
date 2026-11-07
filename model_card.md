# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

The recommender works like a judge giving every song in the catalog a score out of 7, then handing back the highest scorers.

**What it knows about a song:** its genre, its mood, how energetic it is (0 to 1), and how acoustic it is (0 to 1). **What it knows about you:** your favorite genre, your favorite mood, the energy level you want, and whether you prefer acoustic or electronic sounds.

**How a song earns points:**
- If the song's mood is the one you asked for, it gets 2 points.
- If its genre is the one you asked for, it gets 1 point.
- For energy, it gets up to 3 points based on how *close* the song is to your target, not on whether it is high or low. A song that lands right on your target gets all 3, and the further away it is in either direction, the fewer points it gets. Acousticness works the same way with up to 1 point.

Then the system lines up all the songs from highest score to lowest and shows you the top five, along with the reasons each one scored the way it did ("mood match, +2.00", and so on).

Energy gets the most weight because it is the only feature that comes in degrees, so it separates songs from each other. Mood counts for more than genre because mood describes the situation you are listening in, while genre is a broad label, and two songs in the same genre can feel completely different.

**Changes from the starter:** the starter code only held placeholders. I implemented loading the song file, the scoring rule, the ranking step and the explanations, and I grew the catalog from 10 to 20 songs with new genres and moods.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
