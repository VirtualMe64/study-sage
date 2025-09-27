from manim import *

class ConclusionAndSummary(Scene):
    def construct(self):
        # Title of the scene
        title = Text("Conclusion and Summary", font_size=48)
        self.play(Create(title))
        self.wait(1)

        # Key points to summarize
        de_morgan_laws = MathTex(r"\neg (A \land B) \equiv (\neg A \lor \neg B")
        encouragement = Text("Explore further topics in logic!", font_size=36)

        # Position the key points below the title
        de_morgan_laws.next_to(title, DOWN, buff=0.5)
        encouragement.next_to(de_morgan_laws, DOWN, buff=0.5)

        # Animate the appearance of De Morgan's Laws
        self.play(Write(de_morgan_laws))
        self.wait(2)

        # Animate the removal of De Morgan's Laws letter by letter
        self.play(RemoveTextLetterByLetter(de_morgan_laws))
        self.wait(1)

        # Animate the encouragement text
        self.play(Write(encouragement))
        self.wait(2)

        # Fade out the encouragement text
        self.play(FadeOut(encouragement))
        self.wait(1)

        # Fade out the title
        self.play(FadeOut(title))
        self.wait(1)