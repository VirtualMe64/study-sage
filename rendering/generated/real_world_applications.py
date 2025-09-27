from manim import *

class RealWorldApplications(Scene):
    def construct(self):
        # Title of the scene
        title = Tex(r"\textbf{Real-World Applications of De Morgan's Law}")
        title.scale(1.5)
        self.play(Create(title))
        self.wait(1)

        # Introduction to De Morgan's Law
        intro = Tex(r"\text{De Morgan's Law states:}")
        self.play(ReplacementTransform(title, intro))
        self.wait(1)

        # Displaying De Morgan's Law
        law = MathTex(r"\neg(A \land B) \equiv (\neg A) \lor (\neg B)")
        law.next_to(intro, DOWN)
        self.play(Create(law))
        self.wait(2)

        # Discussing applications in programming
        programming_app = Tex(r"\text{Applications in Programming:}")
        programming_app.next_to(law, DOWN)
        self.play(ReplacementTransform(law, programming_app))
        self.wait(1)

        # Example of programming application
        example_code = Tex(r"\text{if } \neg(A \land B) \text{ then } \neg A \lor \neg B").next_to(programming_app, DOWN)
        self.play(Create(example_code))
        self.wait(2)

        # Transition to logic circuits
        logic_circuits = Tex(r"\text{Applications in Logic Circuits:}")
        logic_circuits.next_to(example_code, DOWN)
        self.play(ReplacementTransform(example_code, logic_circuits))
        self.wait(1)

        # Example of logic circuit application
        circuit_example = MathTex(r"\text{NOT}(A \land B) \equiv \text{NOT } A \lor \text{NOT } B").next_to(logic_circuits, DOWN)
        self.play(Create(circuit_example))
        self.wait(2)

        # Conclusion about importance
        conclusion = Tex(r"\text{Importance: Simplifying Expressions}")
        conclusion.next_to(circuit_example, DOWN)
        self.play(ReplacementTransform(circuit_example, conclusion))
        self.wait(1)

        # Final wait before ending the scene
        self.wait(2)