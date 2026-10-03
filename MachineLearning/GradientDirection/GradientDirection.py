from manim import *
import numpy as np


class GradientVisualizer3D(ThreeDScene):

    def construct(self):
        # ---------------------------------------------------------
        # 1. Camera & Scene Setup
        # ---------------------------------------------------------
        self.set_camera_orientation(phi=65 * DEGREES, theta=-55 * DEGREES)
        self.camera.frame_center = np.array([0, -0.2, 0])

        # Compact 3D Axes
        axes = ThreeDAxes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-2.5, 2.5, 1],
            z_range=[-1, 4, 1],
            x_length=4.2,
            y_length=4.2,
            z_length=3.2,
        ).move_to(ORIGIN)

        labels = axes.get_axis_labels(x_label="x", y_label="y", z_label="z")

        # ---------------------------------------------------------
        # 2. Fixed 2D Overlay Elements (UI)
        # ---------------------------------------------------------
        title = Text("Gradient Direction  \u2207f(x, y)", font_size=24)
        title.to_corner(UL)

        text_box = Rectangle(
            width=7.5,
            height=1.5,
            fill_color=BLACK,
            fill_opacity=0.85,
            stroke_color=WHITE,
            stroke_width=1.5,
        ).to_corner(DL)

        # Inizializziamo l'oggetto testo principale per le spiegazioni
        self.current_text = Text(
            "Visualizing 3D Scalar Fields", font_size=16, color=YELLOW
        ).move_to(text_box)

        # Fissiamo TUTTA la UI alla schermata 2D fin da subito
        self.add_fixed_in_frame_mobjects(title, text_box, self.current_text)

        # Display axes
        self.play(Create(axes), Write(labels))

        # Helper per cambiare testo SENZA sovrapposizioni o perdite nel piano 3D
        def update_explanation(new_string, color=WHITE, font_size=16):
            lines = new_string.split("\n")
            if len(lines) > 1:
                new_text_mobj = Paragraph(
                    *lines,
                    font_size=font_size,
                    color=color,
                    alignment="center",
                )
            else:
                new_text_mobj = Text(
                    new_string, font_size=font_size, color=color
                )

            new_text_mobj.move_to(text_box)

            # Rendi fisso il nuovo testo prima di animare
            self.add_fixed_in_frame_mobjects(new_text_mobj)

            # Dissolvenza incrociata pulita
            self.play(
                FadeOut(self.current_text, run_time=0.3),
                FadeIn(new_text_mobj, run_time=0.3),
            )
            # Aggiorna il riferimento all'oggetto testo attivo
            self.current_text = new_text_mobj

        # ---------------------------------------------------------
        # 3. Core Function Visualizer
        # ---------------------------------------------------------
        def animate_function(
            func_lambda,
            grad_lambda,
            func_title_text,
            x0,
            y0,
            contour_r_list,
            is_saddle=False,
        ):

            # Step A: Function Title
            update_explanation(f"Function: {func_title_text}", color=GREEN)

            # Draw 3D Surface
            surface = Surface(
                lambda u, v: axes.c2p(u, v, func_lambda(u, v)),
                u_range=[-2, 2],
                v_range=[-2, 2],
                resolution=(24, 24),
            )
            surface.set_style(fill_opacity=0.5, stroke_color=BLUE_E)
            surface.set_fill_by_value(
                axes=axes, colorscale=[BLUE, GREEN, YELLOW, RED]
            )

            self.play(Create(surface), run_time=1.5)
            self.wait(0.5)

            # Step B: Level Curves (Contour lines on xy-plane)
            contours = VGroup()
            for r in contour_r_list:
                if not is_saddle:
                    circle = ParametricFunction(
                        lambda t: axes.c2p(r * np.cos(t), r * np.sin(t), 0),
                        t_range=[0, TAU],
                        color=GRAY_B,
                    )
                    contours.add(circle)
                else:
                    t = np.linspace(-1.3, 1.3, 40)
                    if r > 0:
                        x_val = np.sqrt(r) * np.cosh(t)
                        y_val = np.sqrt(r) * np.sinh(t)
                    elif r < 0:
                        x_val = np.sqrt(-r) * np.sinh(t)
                        y_val = np.sqrt(-r) * np.cosh(t)
                    else:
                        continue

                    pts_pos = [
                        axes.c2p(x, y, 0)
                        for x, y in zip(x_val, y_val)
                        if abs(x) <= 2 and abs(y) <= 2
                    ]
                    pts_neg = [
                        axes.c2p(-x, -y, 0)
                        for x, y in zip(x_val, y_val)
                        if abs(x) <= 2 and abs(y) <= 2
                    ]

                    if len(pts_pos) > 1:
                        contours.add(
                            VMobject()
                            .set_points_smoothly(pts_pos)
                            .set_color(GRAY_B)
                        )
                    if len(pts_neg) > 1:
                        contours.add(
                            VMobject()
                            .set_points_smoothly(pts_neg)
                            .set_color(GRAY_B)
                        )

            update_explanation(
                "Gray lines = Level curves (contour lines on xy-plane)",
                color=WHITE,
            )
            self.play(Create(contours))
            self.wait(1)

            # Step C: Point Selection
            z0 = func_lambda(x0, y0)
            gx, gy = grad_lambda(x0, y0)

            pt_xy = Dot3D(point=axes.c2p(x0, y0, 0), color=YELLOW, radius=0.07)
            pt_surf = Dot3D(
                point=axes.c2p(x0, y0, z0), color=RED, radius=0.07
            )
            drop_line = DashedLine(
                start=axes.c2p(x0, y0, 0),
                end=axes.c2p(x0, y0, z0),
                color=YELLOW_D,
            )

            update_explanation(
                "Selecting a point P(x, y) in the domain", color=YELLOW
            )
            self.play(
                FadeIn(pt_xy),
                Create(drop_line),
                FadeIn(pt_surf),
            )
            self.wait(1)

            # Step D: Gradient Vector vs Tangent Vector
            grad_arrow = Arrow3D(
                start=axes.c2p(x0, y0, 0),
                end=axes.c2p(x0 + gx * 0.6, y0 + gy * 0.6, 0),
                color=GOLD,
            )

            surf_arrow = Arrow3D(
                start=axes.c2p(x0, y0, z0),
                end=axes.c2p(
                    x0 + gx * 0.6,
                    y0 + gy * 0.6,
                    z0 + (gx * gx + gy * gy) * 0.3,
                ),
                color=RED,
            )

            update_explanation(
                "The Gradient Vector (GOLD) lies entirely\nin the domain (xy-plane)!",
                color=GOLD,
            )
            self.play(Create(grad_arrow), Create(surf_arrow))
            self.wait(1.5)

            # Step E: Top-down View (Orthogonality)
            self.move_camera(
                phi=0 * DEGREES, theta=-90 * DEGREES, run_time=2.5
            )
            update_explanation(
                "Top view: The Gradient is PERPENDICULAR\nto the level curves!",
                color=ORANGE,
            )
            self.wait(2)

            # Step F: Return to 3D View (Steepest Ascent)
            self.move_camera(
                phi=65 * DEGREES, theta=-30 * DEGREES, run_time=2.5
            )
            update_explanation(
                "The gradient points in the direction of\nSTEEPEST ASCENT on the surface",
                color=RED_B,
            )
            self.wait(2.5)

            # Cleanup for next example
            self.play(
                Uncreate(surface),
                Uncreate(contours),
                FadeOut(pt_xy),
                FadeOut(pt_surf),
                Uncreate(drop_line),
                Uncreate(grad_arrow),
                Uncreate(surf_arrow),
            )

        # ---------------------------------------------------------
        # 4. Run Examples
        # ---------------------------------------------------------

        # --- EXAMPLE 1: Paraboloid ---
        animate_function(
            func_lambda=lambda u, v: 0.4 * (u**2 + v**2),
            grad_lambda=lambda x, y: (0.8 * x, 0.8 * y),
            func_title_text="1) Paraboloid z = f(x, y)",
            x0=1.1,
            y0=1.1,
            contour_r_list=[0.6, 1.0, 1.4, 1.8],
            is_saddle=False,
        )

        # Reset camera orientation for next example
        self.move_camera(phi=65 * DEGREES, theta=-55 * DEGREES, run_time=1)

        # --- EXAMPLE 2: Saddle Surface ---
        animate_function(
            func_lambda=lambda u, v: 0.4 * (u**2 - v**2) + 1.5,
            grad_lambda=lambda x, y: (0.8 * x, -0.8 * y),
            func_title_text="2) Saddle Surface z = f(x, y)",
            x0=1.2,
            y0=0.6,
            contour_r_list=[-1.5, -0.8, 0.8, 1.5],
            is_saddle=True,
        )

        # Summary
        update_explanation(
            "Summary:\n1. Gradient \u2208 xy-plane\n2. \u22a5 to level curves\n3. Points toward maximum growth",
            color=GREEN,
        )
        self.wait(3)