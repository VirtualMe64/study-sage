from manim import *

class VisualizingWithVennDiagrams(Scene):
    def construct(self):
        # Create circles for sets A and B
        circle_a = Circle(radius=1.5, color=BLUE, fill_opacity=0.5).shift(LEFT)
        circle_b = Circle(radius=1.5, color=GREEN, fill_opacity=0.5).shift(RIGHT)

        # Create labels for sets A and B
        label_a = MathTex(r"A").next_to(circle_a, UP)
        label_b = MathTex(r"B").next_to(circle_b, UP)

        # Create the union and intersection labels
        union_label = MathTex(r"A \, \cup \, B").to_edge(UP)
        intersection_label = MathTex(r"A \, \cap \, B").to_edge(DOWN)

        # Create the complement labels
        complement_union_label = MathTex(r"(A \, \cup \, B)'").next_to(union_label, DOWN)
        complement_intersection_label = MathTex(r"(A \, \cap \, B)'").next_to(intersection_label, DOWN)

        # Add circles and labels to the scene
        self.play(Create(circle_a), Create(circle_b), FadeIn(label_a), FadeIn(label_b))
        self.wait(1)

        # Show the union of A and B
        self.play(FadeIn(union_label))
        self.wait(1)

        # Highlight the area of (A ∪ B)'
        union_complement_area = Circle(radius=2, color=YELLOW, fill_opacity=0.5)
        self.play(Create(union_complement_area))
        self.play(FadeIn(complement_union_label))
        self.wait(1)

        # Show the first law: (A ∪ B)' = A' ∩ B'
        self.play(FadeOut(union_complement_area), FadeOut(union_label), FadeOut(complement_union_label))
        self.play(FadeIn(intersection_label))
        self.wait(1)

        # Highlight the area of A' ∩ B'
        intersection_complement_area = Circle(radius=2, color=ORANGE, fill_opacity=0.5)
        self.play(Create(intersection_complement_area))
        self.play(FadeIn(complement_intersection_label))
        self.wait(1)

        # Transition to the second law: (A ∩ B)' = A' ∪ B'
        self.play(FadeOut(intersection_complement_area), FadeOut(intersection_label), FadeOut(complement_intersection_label))
        self.play(FadeIn(union_label))
        self.wait(1)

        # Highlight the area of (A ∩ B)'
        self.play(Create(union_complement_area))
        self.play(FadeIn(complement_union_label))
        self.wait(1)

        # Show the final result
        self.play(FadeOut(union_complement_area), FadeOut(union_label), FadeOut(complement_union_label))
        self.wait(1)

        # End the scene
        self.play(FadeOut(circle_a), FadeOut(circle_b), FadeOut(label_a), FadeOut(label_b))
        self.wait(1)