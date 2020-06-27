from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # Both Cases
    Or(And(AKnight, Not(AKnave)), And(Not(AKnight), AKnave)),
    # Knight tells truth
    Implication(AKnight, And(AKnight, AKnave)),
    # Knave lies
    Implication(AKnave, Not(And(AKnight, AKnave)))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # Both Cases
    Or(And(AKnight, Not(AKnave)), And(Not(AKnight), AKnave)),
    Or(And(BKnight, Not(BKnave)), And(Not(BKnight), BKnave)),
    # Knight tells truth
    Implication(AKnight, And(AKnave, BKnave)),
    # Knave lies
    Implication(Not(AKnight), Not(And(AKnave, BKnave)))
)


# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # Both Cases
    Or(And(AKnight, Not(AKnave)), And(Not(AKnight), AKnave)),
    Or(And(BKnight, Not(BKnave)), And(Not(BKnight), BKnave)),
    # Knight tells truth
    Implication(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    Implication(BKnight, Or(And(AKnight, Not(BKnight)), And(Not(AKnight), BKnight))),
    # Knave lies 
    Implication(AKnave, Not(Or(And(AKnight, BKnight), And(AKnave, BKnave)))),
    Implication(BKnave, Not(Or(And(AKnight, Not(BKnight)), And(Not(AKnight), BKnight))))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."

# Symbols for A saying whether it is a Knight and Knave
AsaidKnight = Symbol("A said they are a Knight")
AsaidKnave = Symbol("A said they are a Knave")

knowledge3 = And(
    # Both Cases 
    Or(And(AKnight, Not(AKnave)), And(Not(AKnight), AKnave)),
    Or(And(BKnight, Not(BKnave)), And(Not(BKnight), BKnave)),
    Or(And(CKnight, Not(CKnave)), And(Not(CKnight), CKnave)),
    Or(And(AsaidKnight, Not(AsaidKnave)), And(Not(AsaidKnight), AsaidKnave)),
    # Knight tells truth
    Implication(AKnight, AsaidKnight),
    Implication(BKnight, CKnave),
    Implication(BKnight, AsaidKnave),
    Implication(CKnight, AKnight),
    # Knave lies
    Implication(Not(AKnight), AsaidKnight),
    Implication(Not(BKnight), Not(CKnave)),
    Implication(Not(BKnight), Not(AsaidKnave)),
    Implication(Not(CKnight), Not(AKnight))
)

def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
