# Mech 325, Deus ex Machina.

## TO USE THIS REPO

Install Local Latex Compiler.
Install Latex Packages until it can compile `latex_output/main.tex`.
Install Local Python Environment.
Install necessary python Packages with `pip install -r requirements.txt`.

run `git update-index --skip-worktree main.py` and `git update-index --skip-worktree latex_output/solution.tex`. So the specific question being solved is not tracked in the repo.

## TO SOLVE A PROBLEM WITH THIS REPO.

1. Go to examples folder, copy content of the respective file into main.py.
2. Replace the values as you see fit. For more variable names, use `list_vars(context)`.
3. Run `python main.py`
4. Follow through the prompts.
5. Read the answer off from `./latex_output/aux/main.pdf`.

### Expected Behaviour

- Waits a bit to find a path to solve the problem.
- Start asking questions while showing table, figures, or instructions.
- Exits.

### Unexpected Behaviour

If an error is thrown or the program halts Something is wrong.

If there is an issue BEFORE EXAM:

- Please report it ASAP with the "context" you used.

If there is an issue DURING EXAM:

- Save the "context" that cause the problem.
- Forfeit the program, use the bible instead.
- Please report it back to me with the "context".

## Other

Good Luck in MECH 325.

## For those who want to help

Urgent:
Spring Fatigue loading, sinus, zimmerli, etc.

General:

- [ ] Refactor code to deal with iteration more effectively.
- [ ] Decouple a big CUSTOM function.
- [ ] Detect halting and guess missing informaiton.
- [ ] Incorporate in units.

UX:

- [ ] Use description and units of values in a meaningful way.

Main Missing Feature:

- [ ] Wire Rope
- [ ] Spring

Features:
| Main Task | Sub Task | Implemented | Tested | Documented |
|-------------------|-------------------------------|---------------|---------------|---------------|
| FLAT BELT | main question type | x | x | x |
| FLAT BELT | lower constraints | | | |
| V BELT | | x | x | x |
| SYNCHRONOUS BELT | | x | x | |
| CHAIN | | x | x | |
| WIRE ROPE | | | | |
| SPUR GEAR | | x | x | |
| HELICAL GEAR | | x | | |
| BEVEL GEAR | | x | x | |
| WORM GEAR | | x | | |
| RACK PINION | | | | |
| BUSHING | Shigley Selection | x | x | |
| BUSHING | | | | |
| BALL AND CYLINDRICAL BEARING RADIAL | Selection | x | x | |
| BALL AND CYLINDRICAL BEARING RADIAL | Clearance | | | |
| BALL AND CYLINDRICAL BEARING ALL | Selection | x | x | |
| BALL AND CYLINDRICAL BEARING ALL | Clearance | | | |
| TAPER BEARING | Selection | x | x | x |
| TAPER BEARING | Clearance | | | |
| SHAFT | | x | x | |
| KEY | | | | |
| PIN | | | | |
| SET SCREW | | | | |
| POWER SCREW | | x | | |
| BALL SCREW | | x | x | |
| SPRINGS | si | x | x | |
| SPRINGS | imperial | x | | |
| SPRINGS | Zimmerli, Sinus Failure | | | |
| SPRINGS | critical frequency | | | |
| BOLTS | imperial | x | x | |
| BOLTS | si | x | | |
| BOLT JOINT | | x | x | |
