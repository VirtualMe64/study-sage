from manim import *

class IntroductionToDeMorgansLaw(Scene):
    def construct(self):
        # Title of the scene
        title = Text("Introduction to De Morgan's Law", font_size=36)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        # Definition of De Morgan's Law
        definition = MathTex(r"\neg(A \cap B) = \neg A \cup \neg B", font_size=48)
        self.play(Create(definition))
        self.wait(2)

        # Explanation of the definition
        explanation = Text("This means that the negation of the intersection is the union of the negations.", font_size=24)
        explanation.next_to(definition, DOWN)
        self.play(Write(explanation))
        self.wait(3)

        # Importance in mathematics and logic
        importance_title = Text("Importance in Mathematics and Logic", font_size=30)
        importance_title.next_to(explanation, DOWN, buff=1)
        self.play(Create(importance_title))
        self.wait(1)

        importance_points = VGroup(
            Text("1. Simplifies logical expressions.", font_size=24),
            Text("2. Fundamental in set theory.", font_size=24),
            Text("3. Used in computer science and programming.", font_size=24)
        )
        importance_points.arrange(DOWN, buff=0.5)
        importance_points.next_to(importance_title, DOWN)

        # Animate each point with a delay
        for point in importance_points:
            self.play(Write(point))
            self.wait(1)

        # Final message
        final_message = Text("Understanding De Morgan's Law is crucial!", font_size=28)
        final_message.next_to(importance_points, DOWN, buff=1)
        self.play(Create(final_message))
        self.wait(2)

        # End of the scene
        self.play(FadeOut(importance_points), FadeOut(final_message))
        self.wait(1)