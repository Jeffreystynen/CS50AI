import sys

from crossword import *
import copy


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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
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
        for v in self.domains.keys():
            for x in self.domains[v].copy():
                if v.length != len(x):
                    self.domains[v].remove(x)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        print("REVISING...")
        # revised = False
        # for word in self.domains[x].copy():
        #     overlap = self.crossword.overlaps.get((word, y))
        #     print(overlap)
        #     if overlap is None:
        #         self.domains[x].remove(word)
        #         revised = True
        # return revised
    

        revision_complete = False
        domains_copy = copy.deepcopy(self.domains)
        overlap = self.crossword.overlaps[x, y]

        if overlap is None:
            return False
        else:
            x_overlap, y_overlap = overlap
            for x_word in domains_copy[x]:
                # There is no x variable that overlaps with y variable
                no_overlap = True
                for y_word in domains_copy[y]:
                    if x_word != y_word and x_word[x_overlap] == y_word[y_overlap]:
                        no_overlap = False
                        break
                if no_overlap:
                    self.domains[x].remove(x_word)
                    revision_complete = True

        return revision_complete


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        print("USING ac3...")
        if arcs is None:
            queue = []
            for var_1 in self.domains:
                for var_2 in self.domains:
                    if var_1 != var_2:
                        queue.append((var_1, var_2))
        else:
            queue = arcs
        while queue:
            x, y = queue.pop()
            if self.revise(x,y):
                if not self.domains[x]:
                    return False
                else:
                    for z in self.crossword.neighbors(x) - {y}:
                        queue.append((z,x))


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.domains:
            if variable not in assignment.keys():
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        used_val = []
        for var_x in assignment:
            val_x = assignment[var_x]

            if val_x in used_val:
                return False
            used_val.append(val_x)

            if var_x.length != len(val_x):
                return False
            
            for var_y in self.crossword.neighbors(var_x):
                if var_y in assignment:
                    overlap = self.crossword.overlaps[(var_x, var_y)]
                    if val_x[overlap[0]] != assignment[var_y][overlap[1]]:
                        return False
                    
        return True  

            

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # count_dict = {val: 0 for val in self.domains[var]}
        # print("Domains for variable", var, ":", self.domains[var])

        # for neighbor_var in self.crossword.neighbors(var):
        #     if neighbor_var not in assignment:
        #         for val in self.domains[neighbor_var]:
        #             overlap = self.crossword.overlaps[var, neighbor_var]
        #             if overlap:
        #                 if any(val[overlap[0]] != other_val[overlap[1]] for other_val in self.domains[neighbor_var]):
        #                     if val in count_dict:
        #                         count_dict[val] += 1
        #                 print("Current Val:", val)
        # print("Count Dict:", count_dict) 
        # return sorted(self.domains[var], key=lambda val: count_dict[val])




         # iterate through neighbours
        neighbours = self.crossword.neighbors(var)
        for variable in assignment:
            # If variable is in both neighbors and assignment, no longer neighbour
            if variable in neighbours:
                neighbours.remove(variable)

        # Initialize a list for sorting from the least constraining values
        result = []

        for variable in self.domains[var]:
            # total number of ruled out
            total = 0
            for neighbour in neighbours:
                for value in self.domains[neighbour]:
                    overlap = self.crossword.overlaps[var, neighbour]

                    # if there is an overlap between variables
                    if overlap:
                        a, b = overlap
                        if variable[a] != value[b]:
                            total += 1
            result.append([variable, total])

        result.sort(key=lambda x: x[1])
        return [i[0] for i in result]
            

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_var = []

        for var in self.crossword.variables:
            if var not in assignment:
                unassigned_var.append(var)
        if not unassigned_var:
            return None  # If all variables are assigned, return None

        # Sort unassigned variables based on the number of remaining values in their domain
        unassigned_var.sort(key=lambda var: len(self.domains[var]))

        # Return the variable with the minimum remaining values
        return unassigned_var[0]        


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        print("BACKTRACKING...")
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = copy.deepcopy(assignment)
            new_assignment[var] = value
            if self.consistent(new_assignment):
                assignment[var] = value
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            assignment.pop(var, None)
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
