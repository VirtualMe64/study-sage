from manim import *

class LogicalExpressionsAndTruthTables(Scene):
    def construct(self):
        # Title of the scene
        title = Text("Logical Expressions and Truth Tables", font_size=36)
        self.play(FadeIn(title))
        self.wait(1)
        self.play(FadeOut(title))

        # De Morgan's Laws
        law1 = MathTex(r"\neg (A \land B) \equiv (\neg A) \lor (\neg B)")
        law2 = MathTex(r"\neg (A \lor B) \equiv (\neg A) \land (\neg B")
        self.play(Create(law1))
        self.wait(2)
        self.play(Transform(law1, law2))
        self.wait(2)

        # Create truth tables
        table1 = MathTex(r"\begin{array}{|c|c|c|c|}
        \hline
        A & B & \neg (A \land B) & (\neg A) \lor (\neg B) \\
        \hline
        T & T & F & F \\
        T & F & T & T \\
        F & T & T & T \\
        F & F & T & T \\
        \hline
        \end{array}")
        table2 = MathTex(r"\begin{array}{|c|c|c|c|}
        \hline
        A & B & \neg (A \lor B) & (\neg A) \land (\neg B) \\
        \hline
        T & T & F & F \\
        T & F & F & F \\
        F & T & F & F \\
        F & F & T & T \\
        \hline
        \end{array}")

        # Display the first truth table
        self.play(Create(table1))
        self.wait(3)

        # Transition to the second truth table
        self.play(Transform(table1, table2))
        self.wait(3)

        # Conclusion
        conclusion = Text("De Morgan's Laws are fundamental in logic!", font_size=24)
        self.play(FadeIn(conclusion))
        self.wait(2)
        self.play(FadeOut(conclusion))
        self.wait(1)