# guitarBot

This repo is a part of my master's project at the Robotics Musicianship Lab, GTCMT. It contains different implementations to work the guitar robot.

1. MIDI playback: Input any midifile to play it back on the guitar robot
2. Super-human capability demonstration: The system can read multiple voicings from any given choarle by JS Bach and can play all of them simultaneuosly on the guitar robot. This demonstration was built to explore super-human playing capabilities of the robot as its fretting hand is different from that of a human
3. A basic autoencoder trained on Wikifonia Lead sheets dataset for accompaniment generation to any given melody.

These things were developed in my first semester and provided a basis for me to explore my actual research question:
Can we build a system that learns a robot's physical constraints and composes music suited to its embodiment, instead of what a human would play?

Currently we can run the following demos:

demo.py: 
- Users can first select whether they want to demo single chords or chord progressions. User can also decide if they want humanPlayable or bot's chords.
- Single chord: This script inputs the root and chordType from the user and loops four different vesions selected at random from the database. The user can then input another chord or the same one. 
- Multiple chords: This script inputs the chord progression from the user and loops four different vesions selected at random from the database. The user can then input another chord progression or the same one.