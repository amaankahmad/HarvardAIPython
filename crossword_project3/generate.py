import sys
import math
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables: # Iterate through the variables
            for word in self.crossword.words: # Iterate through the words
                if var.length != len(word):
                    self.domains[var].remove(word) # Remove words with different length
                

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x,y] # Obtain the overlap of x and y
        if overlap != None:
            i, j = overlap
            for wordX in self.domains[x]:
                overlap_possible = False
                for wordY in self.domains[y]:
                    if wordX != wordY and wordX[i] == wordY[j]:
                        overlap_possible = True
                        break
                if not overlap_possible:
                    self.domains[x].remove(wordX)
                    return True
        return False


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = [] # Initialise list of arcs
            for var1 in self.crossword.variables:
                for var2 in self.crossword.neighbors(var1):
                    arcs.append((var1, var2))

        for x, y in arcs:
            if self.revise(x,y): # Check if revisions were made
                for neighbour in self.crossword.neighbors(x): #- {y}:
                    arcs.append((x, neighbour))

        if len(self.domains[x]) > 0: # No Domains empty
            return True
        else: 
            return False


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment.keys():
                return False    
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var1 in assignment.keys():
            word1 = assignment[var1] # Obtain the word if selected
            if var1.length != len(word1): # Word doesn't fit 
                return False
            for var2 in assignment.keys(): # Check if word unique
                if var1 != var2: # Check variables aren't the same
                    word2 = assignment[var2] # Obtain other word in crossword
                    if word1 == word2: # Words aren't unique
                        return False
                    overlap = self.crossword.overlaps[var1, var2] 
                    if overlap != None: # Check if they overlap
                        i, j = overlap 
                        if word1[i] != word2[j]: # Check overlap is the same letter
                            return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        ordered_neighbours = {} # Ordered dictionary of neighbouring variables
        for value in self.domains[var]:
            if value in assignment: # Move onto next value
                continue
            else:
                counter = 0
                for neighbour in self.crossword.neighbors(var):
                    if value in self.domains[neighbour]: # If value in neighbour domain
                        counter += 1
                ordered_neighbours[value] = counter
        return sorted(ordered_neighbours, key = lambda k: ordered_neighbours[k])


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = set(self.domains.keys()) - set(assignment.keys()) # Create a set of unassigned variables
        degrees = 0
        value = math.inf

        for var in unassigned:
            if len(self.domains[var]) < value: # Less values
                value = len(self.domains[var])
                next_variable = var
            elif len(self.domains[var]) == value:
                if self.crossword.neighbors(var) != None:
                    degrees2 = len(self.crossword.neighbors(var)) 
                    if degrees2 > degrees: # More neighbours
                        degrees = degrees2
                        next_variable = var
                        value = len(self.domains[var])
        return next_variable


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment # Completed
        var = self.select_unassigned_variable(assignment) # Obtain the next best variable
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value # Assign valuables to the variable 
            if self.consistent(assignment): # Consistent with the constraints
                result = self.backtrack(assignment)
                if result is None:
                    assignment[var] = None
                else:
                    return result
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
