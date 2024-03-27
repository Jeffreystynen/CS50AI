import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count and self.count !=0:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If the sentence is not empty and the count is 0 which means that there are no bombs in the sentence.
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
            return 1
        return 0

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            return 1
        return 0


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1)
        self.moves_made.add(cell)

        # 2)
        self.mark_safe(cell)
        
        # 3)
        minesCount = 0
        undetermined = []

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) in self.mines:
                    minesCount += 1
                if 0 <= i < self.height and 0 <= j < self.width and (i, j) not in self.safes and (i, j) not in self.moves_made:
                    undetermined.append((i, j))
                
        newSentence = Sentence(undetermined, count - minesCount)
        self.knowledge.append(newSentence)

        # 4)
        # Loop over all sentences
        for sentence in self.knowledge:
            # Check if there are mines in the sentence
            if sentence.known_mines():
                # Loop over all the mines and mark them
                for cell in sentence.known_mines().copy():
                    self.mark_mine(cell)
            # Check if there are safes in the sentence
            if sentence.known_safes():
                # Loop over all the safes and mark them
                for cell in sentence.known_safes().copy():
                    self.mark_safe(cell)


        # 5)
                    
        # Loop over all the sentences
        for sentence in self.knowledge:
            # If the cells of the new the new sentence are a subset of a sentence in the KB and that sentence is not empty and is not equal to the sencetence in the KB
            if newSentence.cells.issubset(sentence.cells) and sentence.count > 0 and newSentence.count > 0 and newSentence != sentence:
                # Take the difference of these cells to form a new sentence and add it to the KB
                subSet = sentence.cells.difference(newSentence.cells)
                newSubsetSentence = Sentence(subSet, sentence.count - newSentence.count)
                self.knowledge.append(newSubsetSentence)

        
                
        # self.inference()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        print("Safe moves:", self.safes)
        print("Mines:", self.mines)
        for move in self.safes:
            # print(f"Checking move: {move}")
            if move not in self.moves_made and move not in self.mines:
                print(f"Found safe move: {move}")
                return move
        return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Prioritize known safe cells. TODO (this is not necesary because this only gets used when there are no safe moves?)
        safe_moves = self.safes - self.moves_made - self.mines
        print("Safe moves:", safe_moves)

        if safe_moves:
            print("Choosing known safe move")
            return random.choice(list(safe_moves))

        # If no known safe moves, fallback to selecting unrevealed cells.
        unrevealed = set(itertools.product(range(self.height), range(self.width))) - self.moves_made - self.mines

        if unrevealed:
            print("Choosing random move")
            return random.choice(list(unrevealed))

        # Return None if no moves are available.
        print("No available moves")
        return None


        
    # def inference(self):
    #     """
    #     Draw new inferences from the knowledge base.
    #     """
    #     new_safes = set()
    #     new_mines = set()
        
    #     # Loop over all known sentences and update the known safes.
    #     for sentence in self.knowledge:
    #         known_safes = sentence.known_safes()
    #         new_safes.update(known_safes)

    #     self.safes = self.safes.union(new_safes)

    #     empty = []

    #     # Make an empty sentence for the first iteration.
    #     s2 = Sentence(set(), 0)
    #     new_knowledge = []

    #     # Loop over all sentences in the knowledge base.
    #     for s1 in self.knowledge:
    #         #Filter empty sentences.
    #         if  len(s1.cells) == 0:
    #             empty.append(s1)
    #         # Compare sentence1 and sentence2.
    #         if s1.cells != s2.cells or s1.count != s2.count:

    #             # Check for overlapping cells
    #             common_cells = s1.cells.intersection(s2.cells)
                
    #             # Deduce mines if counts match and cells overlap
    #             if s1.count - s2.count == len(s1.cells) - len(common_cells):
    #                 print(f"found mine!")
    #                 new_mines.update(common_cells)

    #             # If the cells of sentence2 are a subset of sentence1 we can take the difference in cells and in count.
    #             # This results in a new sentence that contains a smalles number of cells so we can single out the positions of the bombs.
    #             if s1.cells.issubset(s2.cells):
    #                 new_cells = s1.cells - s2.cells
    #                 new_count = s1.count - s2.count
    #                 new_sentence = Sentence(new_cells, new_count)
    #                 new_knowledge.append(new_sentence)
    #         s2 = s1
    #     self.knowledge.extend(new_knowledge)
    #     # Remove empty sentences.
    #     for s in empty:
    #         print(f"Empty sentences: {s}")
    #         self.knowledge.remove(s)



    # def safe_or_mine(self):
    #     for sentence in self.knowledge:
    #         sentence.cells.difference_update(self.safes)
    #         sentence.cells.difference_update(self.mines)
