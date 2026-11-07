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

The system over-rewards loud songs. Nine of the 20 songs have an energy of 0.75 or higher, and energy is worth 3 of the 7 points, so the same few songs keep coming back: Fuego en la Calle appears in 5 of my 7 test lists, and Gym Hero and Storm Runner in 4 each, even for profiles that never asked for them (a rock fan, a sad listener, someone with a genre the catalog does not have). Only 3 songs sit in the middle energy range (0.46 to 0.74), so a listener who wants medium energy gets a scattering of unrelated genres instead of a focused list. The energy score is a straight line, so a song 0.3 away from the target loses just 0.9 of its 3 points, which means a mismatched song is never punished very hard. A request for acoustic sound also barely matters (it is worth 1 point), so an acoustic fan who wants high energy still gets loud electronic tracks.

---

## 7. Evaluation

### Profiles tested

I ran seven profiles and read the top 5 songs for each (the full terminal output is in the README under "Experiments You Tried"):

- **Pop** = High-Energy Pop (pop, happy, energy 0.85, acoustic 0.15)
- **Lofi** = Chill Lofi (lofi, chill, energy 0.38, acoustic 0.80)
- **Rock** = Deep Intense Rock (rock, intense, energy 0.92, acoustic 0.10)
- **SadHigh** = sad but high-energy (blues, sad, energy 0.90), a conflicting request
- **AcousticHigh** = high-energy but fully acoustic (ambient, peaceful, energy 0.95, acoustic 0.95), another conflict
- **NotInCatalog** = a genre and mood the catalog does not have (k-pop, bubbly, energy 0.80)
- **EnergyOnly** = only an energy target of 0.5, nothing else

I also wrote 19 automated tests, ran a weight experiment, and tried one fix (see below).

### What surprised me

- **Gym Hero kept showing up for "happy pop" fans.** In plain terms: the system asks four questions about every song: is the mood right, is the genre right, is the energy close, is the sound as acoustic as you like. A happy pop fan has the right genre and the right energy for Gym Hero. It only fails on mood, because Gym Hero is labelled "intense", not "happy". The catalog only has two pop songs and one indie pop song, so once the happy ones are used up, Gym Hero is still one of the closest matches left. It is like asking a small shop for upbeat pop: after the two pop records, the clerk hands you the loudest thing that is almost pop.
- **The same loud songs fill many lists.** Fuego en la Calle appeared in 5 of the 7 lists, and Gym Hero and Storm Runner in 4 each, because energy carries the most points and many songs are loud.
- **Asking for acoustic sound hardly changed anything.** The AcousticHigh and Rock lists contain the same five songs, only in a different order, because acoustic is worth just 1 point and no song is both loud and acoustic.
- **A label match used to beat what the user actually asked for.** For SadHigh the winner was a slow blues song (energy 0.40) when the user wanted energy 0.90. I added a rule that halves the mood and genre bonuses when energy is more than 0.30 off, plus a warning when nothing fits well. The blues song still wins by a hair, but its score fell from 4.50 to 3.00 out of 6.00 and the output now warns the user. For AcousticHigh, a quiet classical piece no longer wins.
- **Chill Lofi gave exactly the list I would pick by hand:** Library Rain, Midnight Coding, Spacewalk Thoughts and Focus Flow.

### Weight experiment: double energy, halve genre

I set the energy weight from 3 to 6 and the genre weight from 1 to 0.5 (temporarily, by changing the constants in a test script, not in the code). The math stays valid: the maximum score for a full profile becomes 9.5 instead of 7.0, the `max_score` function recalculates this automatically, and no song scored above its maximum (the highest was 9.44 out of 9.5). Result: **6 of 7 profiles gave exactly the same top 5, in the same order.** Only SadHigh changed: Blue Hour Blues dropped out and Storm Runner (energy 0.91) took first place. That is different, not clearly more accurate. It follows the "high-energy" half of the request and ignores the "sad" half. The main lesson is that the recommendations are stable: the winners come from the mood and energy match, not from fragile weight choices.

### Comparing each pair of profiles

"Shared" means how many of the top 5 songs appear in both lists.

| Pair | What changed and why it makes sense |
|---|---|
| Pop vs Lofi | 0 shared. Upbeat pop (energy 0.86 on average) vs quiet lofi (0.37). Opposite tastes get opposite lists, as they should. |
| Pop vs Rock | 3 shared (Gym Hero, Storm Runner, Fuego). Both want loud music, so the loud songs overlap. The #1 differs because mood and genre decide it: happy pop gets Sunrise City, intense rock gets Storm Runner. |
| Pop vs SadHigh | 3 shared. SadHigh gets Blue Hour Blues first (the only sad song), then the same loud filler as Pop. |
| Pop vs AcousticHigh | 3 shared. AcousticHigh gets no pop at all and goes for the loudest songs. The acoustic request barely moves the list. |
| Pop vs NotInCatalog | 3 shared (Sunrise City, Rooftop Lights, Fuego). With no genre or mood to match, the system uses energy 0.80 alone, which happens to land on the same happy pop songs. Reasonable, but partly luck. |
| Pop vs EnergyOnly | 0 shared. Moving the energy target from 0.85 to 0.5 swaps the whole list for mid-energy country, r&b and reggae. |
| Lofi vs Rock | 0 shared. The two extremes (energy 0.37 vs 0.93). |
| Lofi vs SadHigh | 1 shared (Blue Hour Blues). It is the one slow, acoustic, sad song, so it fits both: it is Lofi's #5 for being quiet, and SadHigh's #1 for being sad. |
| Lofi vs AcousticHigh | 0 shared. Both like acoustic sound, but energy is worth three times as much as acousticness, so the loud acoustic fan gets loud songs. |
| Lofi vs NotInCatalog | 0 shared. Quiet (0.37) vs fairly loud (0.79). |
| Lofi vs EnergyOnly | 2 shared (Midnight Coding, Focus Flow). Energy 0.5 sits right next to the lofi songs at 0.40 to 0.42, so some overlap is sensible. |
| Rock vs SadHigh | 4 shared. SadHigh is the Rock list with Blue Hour Blues swapped in for Iron Requiem. The sad mood only pulls in one song. |
| Rock vs AcousticHigh | 5 shared, same songs, different order. Both want energy above 0.9 and the acoustic request is too small to change the set. |
| Rock vs NotInCatalog | 1 shared (Fuego). Rock wants 0.92 and gets metal, edm and rock, while NotInCatalog wants 0.80 and gets happier pop and hip hop. |
| Rock vs EnergyOnly | 0 shared. Energy 0.93 vs 0.47 on average. |
| SadHigh vs AcousticHigh | 4 shared. Both ask for something the catalog cannot give (sad and loud, acoustic and loud), so both fall back on the same loud songs, and both now carry the "no good match" warning. |
| SadHigh vs NotInCatalog | 1 shared (Fuego). SadHigh centers on 0.90 plus one blues song, NotInCatalog on 0.80. |
| SadHigh vs EnergyOnly | 0 shared. 0.81 vs 0.47 on average. |
| AcousticHigh vs NotInCatalog | 1 shared (Fuego). 0.93 vs 0.79 on average. |
| AcousticHigh vs EnergyOnly | 0 shared. 0.93 vs 0.47 on average. |
| NotInCatalog vs EnergyOnly | 0 shared. Both reduce to an energy-only search, so the whole difference is the target: 0.80 vs 0.50. |

Overall, when energy targets are far apart the lists share nothing, which is the behavior I want. The lists also overlap whenever two profiles want loud songs, and that overlap is where the "same loud songs everywhere" problem comes from.

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
