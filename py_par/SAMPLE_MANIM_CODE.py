
# ===== File: ./concat.py =====
import os

def concat_py_files(root_dir, output_file):
    cnt = 0
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for dirpath, _, filenames in os.walk(root_dir):
            if cnt > 3000 : # line cap
                break
            for filename in sorted(filenames):  # sorted for consistency
                if filename.endswith(".py") and filename != os.path.basename(output_file):
                    file_path = os.path.join(dirpath, filename)
                    outfile.write(f"\n# ===== File: {file_path} =====\n")
                    cnt += 1
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        x = infile.read()
                        outfile.write(x)
                        outfile.write("\n")
                        cnt += len(x.split('\n'))

if __name__ == "__main__":
    # Change '.' to your target directory
    concat_py_files(".", "SAMPLE_MANIM_CODE.py")


# ===== File: ./manim_imports_ext.py =====
from manimlib import *
from manimlib.mobject.svg.old_tex_mobject import *

from custom.backdrops import *
from custom.banner import *
from custom.characters.pi_creature import *
from custom.characters.pi_creature_animations import *
from custom.characters.pi_creature_scene import *
from custom.deprecated import *
from custom.drawings import *
from custom.end_screen import *
from custom.filler import *
from custom.logo import *
from custom.opening_quote import *


# ===== File: ./stage_scenes.py =====
#!/usr/bin/env python
import inspect
import os
import sys
import importlib

from manimlib.config import get_module
from manimlib.extract_scene import is_child_scene


def get_sorted_scene_classes(module_name):
    module = get_module(module_name)
    if hasattr(module, "SCENES_IN_ORDER"):
        return module.SCENES_IN_ORDER
    # Otherwise, deduce from the order in which
    # they're defined in a file
    importlib.import_module(module.__name__)
    line_to_scene = {}
    name_scene_list = inspect.getmembers(
        module,
        lambda obj: is_child_scene(obj, module)
    )
    for name, scene_class in name_scene_list:
        if inspect.getmodule(scene_class).__name__ != module.__name__:
            continue
        lines, line_no = inspect.getsourcelines(scene_class)
        line_to_scene[line_no] = scene_class
    return [
        line_to_scene[index]
        for index in sorted(line_to_scene.keys())
    ]


def stage_scenes(module_name):
    scene_classes = get_sorted_scene_classes(module_name)
    if len(scene_classes) == 0:
        print("There are no rendered animations from this module")
        return
    # TODO, fix this
    animation_dir = os.path.join(
        os.path.expanduser('~'),
        "Dropbox/3Blue1Brown/videos/2021/holomorphic_dynamics/videos"
    )
    # 
    files = os.listdir(animation_dir)
    sorted_files = []
    for scene_class in scene_classes:
        scene_name = scene_class.__name__
        clips = [f for f in files if f.startswith(scene_name + ".")]
        for clip in clips:
            sorted_files.append(os.path.join(animation_dir, clip))
        # Partial movie file directory
        # movie_dir = get_movie_output_directory(
        #     scene_class, **output_directory_kwargs
        # )
        # if os.path.exists(movie_dir):
        #     for extension in [".mov", ".mp4"]:
        #         int_files = get_sorted_integer_files(
        #             pmf_dir, extension=extension
        #         )
        #         for file in int_files:
        #             sorted_files.append(os.path.join(pmf_dir, file))
        # else:

    # animation_subdir = os.path.dirname(animation_dir)
    count = 0
    while True:
        staged_scenes_dir = os.path.join(
            animation_dir,
            os.pardir,
            "staged_scenes_{}".format(count)
        )
        if not os.path.exists(staged_scenes_dir):
            os.makedirs(staged_scenes_dir)
            break
        # Otherwise, keep trying new names until
        # there is a free one
        count += 1
    for count, f in reversed(list(enumerate(sorted_files))):
        # Going in reversed order means that when finder
        # sorts by date modified, it shows up in the
        # correct order
        symlink_name = os.path.join(
            staged_scenes_dir,
            "Scene_{:03}_{}".format(
                count, f.split(os.sep)[-1]
            )
        )
        os.symlink(f, symlink_name)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("No module given.")
    module_name = sys.argv[1]
    stage_scenes(module_name)


# ===== File: ./_2016/fractal_charm.py =====
from manim_imports_ext import *

class FractalCreation(Scene):
    CONFIG = {
        "fractal_class" : PentagonalFractal,
        "max_order" : 5,
        "transform_kwargs" : {
            "path_arc" : np.pi/6,
            "lag_ratio" : 0.5,
            "run_time" : 2,
        },
        "fractal_kwargs" : {},
    }
    def construct(self):
        fractal = self.fractal_class(order = 0, **self.fractal_kwargs)
        self.play(FadeIn(fractal))
        for order in range(1, self.max_order+1):
            new_fractal = self.fractal_class(
                order = order,
                **self.fractal_kwargs
            )
            fractal.align_data_and_family(new_fractal)
            self.play(Transform(
                fractal, new_fractal,
                **self.transform_kwargs
            ))
            self.wait()
        self.wait()
        self.fractal = fractal

class PentagonalFractalCreation(FractalCreation):
    pass

class DiamondFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : DiamondFractal,
        "max_order" : 6,
        "fractal_kwargs" : {"height" : 6}
    }

class PiCreatureFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : PiCreatureFractal,
        "max_order" : 6,
        "fractal_kwargs" : {"height" : 6},
        "transform_kwargs" : {
            "lag_ratio" : 0,
            "run_time" : 2,
        },
    }
    def construct(self):
        FractalCreation.construct(self)
        fractal = self.fractal
        smallest_pi = fractal[0][0]
        zoom_factor = 0.1/smallest_pi.get_height()
        fractal.generate_target()
        fractal.target.shift(-smallest_pi.get_corner(UP+LEFT))
        fractal.target.scale(zoom_factor)
        self.play(MoveToTarget(fractal, run_time = 10))
        self.wait()

class QuadraticKochFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : QuadraticKoch,
        "max_order" : 5,
        "fractal_kwargs" : {"radius" : 10},
        # "transform_kwargs" : {
        #     "lag_ratio" : 0,
        #     "run_time" : 2,
        # },
    }

class KochSnowFlakeFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : KochSnowFlake,
        "max_order" : 6,
        "fractal_kwargs" : {
            "radius" : 6,
            "num_submobjects" : 100,
        },
        "transform_kwargs" : {
            "lag_ratio" : 0.5,
            "path_arc" : np.pi/6,
            "run_time" : 2,
        },
    }

class WonkyHexagonFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : WonkyHexagonFractal,
        "max_order" : 5,
        "fractal_kwargs" : {"height" : 6},
    }

class SierpinskiFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : Sierpinski,
        "max_order" : 6,
        "fractal_kwargs" : {"height" : 6},
        "transform_kwargs" : {
            "path_arc" : 0,
        },
    }

class CircularFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : CircularFractal,
        "max_order" : 5,
        "fractal_kwargs" : {"height" : 6},
    }
    


# ===== File: ./_2016/hanoi.py =====
from manim_imports_ext import *

class CountingScene(Scene):
    CONFIG = {
        "base" : 10,
        "power_colors" : [YELLOW, MAROON_B, RED, GREEN, BLUE, PURPLE_D],
        "counting_dot_starting_position" : (FRAME_X_RADIUS-1)*RIGHT + (FRAME_Y_RADIUS-1)*UP,
        "count_dot_starting_radius" : 0.5,
        "dot_configuration_height" : 2,
        "ones_configuration_location" : UP+2*RIGHT,
        "num_scale_factor" : 2,
        "num_start_location" : 2*DOWN,
    }
    def setup(self):
        self.dots = VGroup()
        self.number = 0        
        self.number_mob = VGroup(OldTex(str(self.number)))
        self.number_mob.scale(self.num_scale_factor)
        self.number_mob.shift(self.num_start_location)
        self.digit_width = self.number_mob.get_width()

        self.initialize_configurations()
        self.arrows = VGroup()
        self.add(self.number_mob)

    def get_template_configuration(self):
        #This should probably be replaced for non-base-10 counting scenes
        down_right = (0.5)*RIGHT + (np.sqrt(3)/2)*DOWN
        result = []
        for down_right_steps in range(5):
            for left_steps in range(down_right_steps):
                result.append(
                    down_right_steps*down_right + left_steps*LEFT
                )
        return reversed(result[:self.base])

    def get_dot_template(self):
        #This should be replaced for non-base-10 counting scenes
        down_right = (0.5)*RIGHT + (np.sqrt(3)/2)*DOWN
        dots = VGroup(*[
            Dot(
                point, 
                radius = 0.25,
                fill_opacity = 0,
                stroke_width = 2,
                stroke_color = WHITE,
            )
            for point in self.get_template_configuration()
        ])
        dots[-1].set_stroke(width = 0)
        dots.set_height(self.dot_configuration_height)
        return dots

    def initialize_configurations(self):
        self.dot_templates = []
        self.dot_template_iterators = []
        self.curr_configurations = []

    def add_configuration(self):
        new_template = self.get_dot_template()
        new_template.move_to(self.ones_configuration_location)
        left_vect = (new_template.get_width()+LARGE_BUFF)*LEFT
        new_template.shift(
            left_vect*len(self.dot_templates)
        )
        self.dot_templates.append(new_template)
        self.dot_template_iterators.append(
            it.cycle(new_template)
        )
        self.curr_configurations.append(VGroup())

    def count(self, max_val, run_time_per_anim = 1):
        for x in range(max_val):
            self.increment(run_time_per_anim)

    def increment(self, run_time_per_anim = 1, added_anims = [], total_run_time = None):
        run_all_at_once = (total_run_time is not None)
        if run_all_at_once:
            num_rollovers = self.get_num_rollovers()
            run_time_per_anim = float(total_run_time)/(num_rollovers+1)
        moving_dot = Dot(
            self.counting_dot_starting_position,
            radius = self.count_dot_starting_radius,
            color = self.power_colors[0],
        )
        moving_dot.generate_target()
        moving_dot.set_fill(opacity = 0)

        continue_rolling_over = True
        place = 0
        self.number += 1
        added_anims = list(added_anims) #Silly python objects...
        added_anims += self.get_new_configuration_animations()
        while continue_rolling_over:          
            moving_dot.target.replace(
                next(self.dot_template_iterators[place])
            )
            if run_all_at_once:
                denom = float(num_rollovers+1)
                start_t = place/denom
                def get_modified_rate_func(anim):
                    return lambda t : anim.original_rate_func(
                        start_t + t/denom
                    )
                for anim in added_anims:
                    if not hasattr(anim, "original_rate_func"):
                        anim.original_rate_func = anim.rate_func
                    anim.rate_func = get_modified_rate_func(anim)
            self.play(
                MoveToTarget(moving_dot), 
                *added_anims, 
                run_time = run_time_per_anim
            )
            self.curr_configurations[place].add(moving_dot)
            if not run_all_at_once:
                added_anims = []


            if len(self.curr_configurations[place].split()) == self.base:
                full_configuration = self.curr_configurations[place]
                self.curr_configurations[place] = VGroup()
                place += 1
                center = full_configuration.get_center_of_mass()
                radius = 0.6*max(
                    full_configuration.get_width(),
                    full_configuration.get_height(),
                )
                circle = Circle(
                    radius = radius,
                    stroke_width = 0,
                    fill_color = self.power_colors[place],
                    fill_opacity = 0.5,
                )
                circle.move_to(center)
                moving_dot = VGroup(circle, full_configuration)
                moving_dot.generate_target()
                moving_dot[0].set_fill(opacity = 0)
            else:
                continue_rolling_over = False
        self.play(*self.get_digit_increment_animations())

    def get_new_configuration_animations(self):
        if self.is_perfect_power():
            self.add_configuration()
            return [FadeIn(self.dot_templates[-1])]
        else:
            return []

    def get_digit_increment_animations(self):
        result = []
        new_number_mob = self.get_number_mob(self.number)
        new_number_mob.move_to(self.number_mob, RIGHT)
        if self.is_perfect_power():
            place = len(new_number_mob.split())-1
            arrow = Arrow(
                new_number_mob[place].get_top(),
                self.dot_templates[place].get_bottom(),
                color = self.power_colors[place]
            )
            self.arrows.add(arrow)
            result.append(ShowCreation(arrow))
        result.append(Transform(
            self.number_mob, new_number_mob,
            lag_ratio = 0.5
        ))
        return result

    def get_number_mob(self, num):
        result = VGroup()
        place = 0
        while num > 0:
            digit = OldTex(str(num % self.base))
            if place >= len(self.power_colors):
                self.power_colors += self.power_colors
            digit.set_color(self.power_colors[place])
            digit.scale(self.num_scale_factor)
            digit.move_to(result, RIGHT)
            digit.shift(place*(self.digit_width+SMALL_BUFF)*LEFT)
            result.add(digit)
            num /= self.base
            place += 1
        return result

    def is_perfect_power(self):
        number = self.number
        while number > 1:
            if number%self.base != 0:
                return False
            number /= self.base
        return True

    def get_num_rollovers(self):
        next_number = self.number + 1
        result = 0
        while next_number%self.base == 0:
            result += 1
            next_number /= self.base
        return result

class BinaryCountingScene(CountingScene):
    CONFIG = {
        "base" : 2,
        "dot_configuration_height" : 1,
        "ones_configuration_location" : UP+5*RIGHT
    }
    def get_template_configuration(self):
        return [ORIGIN, UP]

class CountInDecimal(CountingScene):
    def construct(self):
        for x in range(11):
            self.increment()
        for x in range(85):
            self.increment(0.25)
        for x in range(20):
            self.increment()

class CountInTernary(CountingScene):
    CONFIG = {
        "base" : 3,
        "dot_configuration_height" : 1,
        "ones_configuration_location" : UP+4*RIGHT
    }
    def construct(self):
        self.count(27)

    # def get_template_configuration(self):
    #     return [ORIGIN, UP]

class CountTo27InTernary(CountInTernary):
    def construct(self):
        for x in range(27):
            self.increment()
        self.wait()

class CountInBinaryTo256(BinaryCountingScene):
    def construct(self):
        self.count(256, 0.25)

class TowersOfHanoiScene(Scene):
    CONFIG = {
        "disk_start_and_end_colors" : [BLUE_E, BLUE_A],
        "num_disks" : 5,
        "peg_width" : 0.25,
        "peg_height" : 2.5,
        "peg_spacing" : 4,
        "include_peg_labels" : True,
        "middle_peg_bottom" : 0.5*DOWN,
        "disk_height" : 0.4,
        "disk_min_width" : 1,
        "disk_max_width" : 3,
        "default_disk_run_time_off_peg" : 1,
        "default_disk_run_time_on_peg" : 2,
    }
    def setup(self):
        self.add_pegs()
        self.add_disks()

    def add_pegs(self):
        peg = Rectangle(
            height = self.peg_height,
            width = self.peg_width, 
            stroke_width = 0,
            fill_color = GREY_BROWN,
            fill_opacity = 1,
        )
        peg.move_to(self.middle_peg_bottom, DOWN)
        self.pegs = VGroup(*[
            peg.copy().shift(vect)
            for vect in (self.peg_spacing*LEFT, ORIGIN, self.peg_spacing*RIGHT)
        ])
        self.add(self.pegs)
        if self.include_peg_labels:
            self.peg_labels = VGroup(*[
                OldTex(char).next_to(peg, DOWN)
                for char, peg in zip("ABC", self.pegs)
            ])
            self.add(self.peg_labels)

    def add_disks(self):
        self.disks = VGroup(*[
            Rectangle(
                height = self.disk_height,
                width = width,
                fill_color = color,
                fill_opacity = 0.8,
                stroke_width = 0,
            )
            for width, color in zip(
                np.linspace(
                    self.disk_min_width, 
                    self.disk_max_width,
                    self.num_disks
                ),
                color_gradient(
                    self.disk_start_and_end_colors,
                    self.num_disks
                )
            )
        ])
        for number, disk in enumerate(self.disks):
            label = OldTex(str(number))
            label.set_color(BLACK)
            label.set_height(self.disk_height/2)
            label.move_to(disk)
            disk.add(label)
            disk.label = label
        self.reset_disks(run_time = 0)

        self.add(self.disks)

    def reset_disks(self, **kwargs):
        self.disks.generate_target()
        self.disks.target.arrange(DOWN, buff = 0)
        self.disks.target.move_to(self.pegs[0], DOWN)
        self.play(
            MoveToTarget(self.disks), 
            **kwargs
        )
        self.disk_tracker = [
            set(range(self.num_disks)),
            set([]),
            set([])
        ]

    def disk_index_to_peg_index(self, disk_index):
        for index, disk_set in enumerate(self.disk_tracker):
            if disk_index in disk_set:
                return index
        raise Exception("Somehow this disk wasn't accounted for...")

    def min_disk_index_on_peg(self, peg_index):
        disk_index_set = self.disk_tracker[peg_index]
        if disk_index_set:
            return min(self.disk_tracker[peg_index])
        else:
            return self.num_disks

    def bottom_point_for_next_disk(self, peg_index):
        min_disk_index = self.min_disk_index_on_peg(peg_index)
        if min_disk_index >= self.num_disks:
            return self.pegs[peg_index].get_bottom()
        else:
            return self.disks[min_disk_index].get_top()

    def get_next_disk_0_peg(self):
        curr_peg_index = self.disk_index_to_peg_index(0)
        return (curr_peg_index+1)%3

    def get_available_peg(self, disk_index):
        if disk_index == 0:
            return self.get_next_disk_0_peg()
        for index in range(len(list(self.pegs))):
            if self.min_disk_index_on_peg(index) > disk_index:
                return index
        raise Exception("Tower's of Honoi rule broken: No available disks")

    def set_disk_config(self, peg_indices):
        assert(len(peg_indices) == self.num_disks)
        self.disk_tracker = [set([]) for x in range(3)]
        for n, peg_index in enumerate(peg_indices):
            disk_index = self.num_disks - n - 1
            disk = self.disks[disk_index]
            peg = self.pegs[peg_index]
            disk.move_to(peg.get_bottom(), DOWN)
            n_disks_here = len(self.disk_tracker[peg_index])
            disk.shift(disk.get_height()*n_disks_here*UP)
            self.disk_tracker[peg_index].add(disk_index)

    def move_disk(self, disk_index, **kwargs):
        next_peg_index = self.get_available_peg(disk_index)
        self.move_disk_to_peg(disk_index, next_peg_index, **kwargs)

    def move_subtower_to_peg(self, num_disks, next_peg_index, **kwargs):
        disk_indices = list(range(num_disks))
        peg_indices = list(map(self.disk_index_to_peg_index, disk_indices))
        if len(set(peg_indices)) != 1:
            warnings.warn("These disks don't make up a tower right now")
        self.move_disks_to_peg(disk_indices, next_peg_index, **kwargs)

    def move_disk_to_peg(self, disk_index, next_peg_index, **kwargs):
        self.move_disks_to_peg([disk_index], next_peg_index, **kwargs)

    def move_disks_to_peg(self, disk_indices, next_peg_index, run_time = None, stay_on_peg = True, added_anims = []):
        if run_time is None:
            if stay_on_peg is True:
                run_time = self.default_disk_run_time_on_peg
            else:
                run_time = self.default_disk_run_time_off_peg
        disks = VGroup(*[self.disks[index] for index in disk_indices])
        max_disk_index = max(disk_indices)
        next_peg = self.pegs[next_peg_index]        
        curr_peg_index = self.disk_index_to_peg_index(max_disk_index)
        curr_peg = self.pegs[curr_peg_index]
        if self.min_disk_index_on_peg(curr_peg_index) != max_disk_index:
            warnings.warn("Tower's of Hanoi rule broken: disk has crap on top of it")
        target_bottom_point = self.bottom_point_for_next_disk(next_peg_index)
        path_arc = np.sign(curr_peg_index-next_peg_index)*np.pi/3
        if stay_on_peg:
            self.play(
                Succession(
                    ApplyMethod(disks.next_to, curr_peg, UP, 0),
                    ApplyMethod(disks.next_to, next_peg, UP, 0, path_arc = path_arc),
                    ApplyMethod(disks.move_to, target_bottom_point, DOWN),
                ),
                *added_anims,
                run_time = run_time,
                rate_func = lambda t : smooth(t, 2)
            )
        else:
            self.play(
                ApplyMethod(disks.move_to, target_bottom_point, DOWN),
                *added_anims,
                path_arc = path_arc*2,
                run_time = run_time,
                rate_func = lambda t : smooth(t, 2)
            )
        for disk_index in disk_indices:
            self.disk_tracker[curr_peg_index].remove(disk_index)
            self.disk_tracker[next_peg_index].add(disk_index)

class ConstrainedTowersOfHanoiScene(TowersOfHanoiScene):
    def get_next_disk_0_peg(self):
        if not hasattr(self, "total_disk_0_movements"):
            self.total_disk_0_movements = 0
        curr_peg_index = self.disk_index_to_peg_index(0)        
        if (self.total_disk_0_movements/2)%2 == 0:
            result = curr_peg_index + 1
        else:
            result = curr_peg_index - 1
        self.total_disk_0_movements += 1
        return result

def get_ruler_sequence(order = 4):
    if order == -1:
        return []
    else:
        smaller = get_ruler_sequence(order - 1)
        return smaller + [order] + smaller

def get_ternary_ruler_sequence(order = 4):
    if order == -1:
        return []
    else:
        smaller = get_ternary_ruler_sequence(order-1)
        return smaller+[order]+smaller+[order]+smaller

class SolveHanoi(TowersOfHanoiScene):
    def construct(self):
        self.wait()
        for x in get_ruler_sequence(self.num_disks-1):
            self.move_disk(x, stay_on_peg = False)
        self.wait()

class SolveConstrainedHanoi(ConstrainedTowersOfHanoiScene):
    def construct(self):
        self.wait()
        for x in get_ternary_ruler_sequence(self.num_disks-1):
            self.move_disk(x, run_time = 0.5, stay_on_peg = False)
        self.wait()

class Keith(PiCreature):
    CONFIG = {
        "color" : GREEN_D
    }
        
def get_binary_tex_mobs(num_list):
    result = VGroup()
    zero_width = OldTex("0").get_width()
    nudge = zero_width + SMALL_BUFF
    for num in num_list:
        bin_string = bin(num)[2:]#Strip off the "0b" prefix
        bits = VGroup(*list(map(Tex, bin_string)))
        for n, bit in enumerate(bits):
            bit.shift(n*nudge*RIGHT)
        bits.move_to(ORIGIN, RIGHT)
        result.add(bits)
    return result

def get_base_b_tex_mob(number, base, n_digits):
    assert(number < base**n_digits)
    curr_digit = n_digits - 1
    zero = OldTex("0")
    zero_width = zero.get_width()
    zero_height = zero.get_height()
    result = VGroup()
    for place in range(n_digits):
        remainder = number%base
        digit_mob = OldTex(str(remainder))
        digit_mob.set_height(zero_height)
        digit_mob.shift(place*(zero_width+SMALL_BUFF)*LEFT)
        result.add(digit_mob)
        number = (number - remainder)/base
    return result.center()

def get_binary_tex_mob(number, n_bits = 4):
    return get_base_b_tex_mob(number, 2, n_bits)

def get_ternary_tex_mob(number, n_trits = 4):
    return get_base_b_tex_mob(number, 3, n_trits)


####################

class IntroduceKeith(Scene):
    def construct(self):
        morty = Mortimer(mode = "happy")
        keith = Keith(mode = "dance_kick")
        keith_image = ImageMobject("keith_schwarz", invert = False)
        # keith_image = Rectangle()
        keith_image.set_height(FRAME_HEIGHT - 2)
        keith_image.next_to(ORIGIN, LEFT)
        keith.move_to(keith_image, DOWN+RIGHT)
        morty.next_to(keith, buff = LARGE_BUFF, aligned_edge = DOWN)
        morty.make_eye_contact(keith)
        randy = Randolph().next_to(keith, LEFT, LARGE_BUFF, aligned_edge = DOWN)
        randy.shift_onto_screen()

        bubble = keith.get_bubble(SpeechBubble, width = 7)
        bubble.write("01101011 $\\Rightarrow$ Towers of Hanoi")
        zero_width = bubble.content[0].get_width()
        one_width = bubble.content[1].get_width()        
        for mob in bubble.content[:8]:
            if abs(mob.get_width() - zero_width) < 0.01:
                mob.set_color(GREEN)
            else:
                mob.set_color(YELLOW)

        bubble.resize_to_content()
        bubble.pin_to(keith)
        VGroup(bubble, bubble.content).shift(DOWN)

        randy.bubble = randy.get_bubble(SpeechBubble, height = 3)
        randy.bubble.write("Wait, what's \\\\ Towers of Hanoi?")

        title = OldTexText("Keith Schwarz (Computer scientist)")
        title.to_edge(UP)

        self.add(keith_image, morty)
        self.play(Write(title))
        self.play(FadeIn(keith, run_time = 2))
        self.play(FadeOut(keith_image), Animation(keith))
        self.play(Blink(morty))
        self.play(
            keith.change_mode, "speaking",
            keith.set_height, morty.get_height(),
            keith.next_to, morty, LEFT, LARGE_BUFF,
            run_time = 1.5
        )
        self.play(
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(
            morty.change_mode, "pondering",
            morty.look_at, bubble
        )
        self.play(Blink(keith))
        self.wait()
        original_content = bubble.content
        bubble.write("I'm usually meh \\\\ on puzzles")
        self.play(
            keith.change_mode, "hesitant",
            Transform(original_content, bubble.content),
        )
        self.play(
            morty.change_mode, "happy",
            morty.look_at, keith.eyes
        )
        self.play(Blink(keith))
        bubble.write("But \\emph{analyzing} puzzles!")
        VGroup(*bubble.content[3:12]).set_color(YELLOW)
        self.play(
            keith.change_mode, "hooray",
            Transform(original_content, bubble.content)
        )
        self.play(Blink(morty))
        self.wait()
        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "confused",
            randy.look_at, keith.eyes,
            keith.change_mode, "plain",
            keith.look_at, randy.eyes,
            morty.change_mode, "plain",
            morty.look_at, randy.eyes,
            FadeOut(bubble),
            FadeOut(original_content),
            ShowCreation(randy.bubble),
            Write(randy.bubble.content)
        )
        self.play(Blink(keith))
        self.play(
            keith.change_mode, "hooray",
            keith.look_at, randy.eyes
        )
        self.wait()

class IntroduceTowersOfHanoi(TowersOfHanoiScene):
    def construct(self):
        self.clear()
        self.add_title()
        self.show_setup()
        self.note_disk_labels()
        self.show_more_disk_possibility()
        self.move_full_tower()
        self.move_single_disk()
        self.cannot_move_disk_onto_smaller_disk()

    def add_title(self):
        title = OldTexText("Towers of Hanoi")
        title.to_edge(UP)
        self.add(title)
        self.title = title

    def show_setup(self):
        self.pegs.save_state()
        bottom = self.pegs.get_bottom()
        self.pegs.stretch_to_fit_height(0)
        self.pegs.move_to(bottom)
        self.play(
            ApplyMethod(
                self.pegs.restore, 
                lag_ratio = 0.5,
                run_time = 2
            ),
            Write(self.peg_labels)
        )
        self.wait()
        self.bring_in_disks()
        self.wait()

    def bring_in_disks(self):
        peg = self.pegs[0]
        disk_groups = VGroup()
        for disk in self.disks:
            top = Circle(radius = disk.get_width()/2)
            inner = Circle(radius = self.peg_width/2)
            inner.flip()
            top.add_subpath(inner.points)
            top.set_stroke(width = 0)
            top.set_fill(disk.get_color())
            top.rotate(np.pi/2, RIGHT)
            top.move_to(disk, UP)
            bottom = top.copy()
            bottom.move_to(disk, DOWN)
            group = VGroup(disk, top, bottom)
            group.truly_original_state = group.copy()
            group.next_to(peg, UP, 0)
            group.rotate(-np.pi/24, RIGHT)
            group.save_state()
            group.rotate(-11*np.pi/24, RIGHT)
            disk.set_fill(opacity = 0)
            disk_groups.add(group)
        disk_groups.arrange()
        disk_groups.next_to(self.peg_labels, DOWN)
        
        self.play(FadeIn(
            disk_groups, 
            run_time = 2, 
            lag_ratio = 0.5
        ))
        for group in reversed(list(disk_groups)):
            self.play(group.restore)
            self.play(Transform(group, group.truly_original_state))
        self.remove(disk_groups)
        self.add(self.disks)

    def note_disk_labels(self):
        labels = [disk.label for disk in self.disks]
        last = VGroup().save_state()
        for label in labels:
            label.save_state()
            self.play(
                label.scale, 2,
                label.set_color, YELLOW,
                last.restore,
                run_time = 0.5
            )
            last = label
        self.play(last.restore)
        self.wait()

    def show_more_disk_possibility(self):
        original_num_disks = self.num_disks
        original_disk_height = self.disk_height
        original_disks = self.disks
        original_disks_copy = original_disks.copy()

        #Hacky
        self.num_disks = 10
        self.disk_height = 0.3
        self.add_disks()
        new_disks = self.disks
        self.disks = original_disks
        self.remove(new_disks)

        self.play(Transform(self.disks, new_disks))
        self.wait()
        self.play(Transform(self.disks, original_disks_copy))

        self.remove(self.disks)
        self.disks = original_disks_copy
        self.add(self.disks)
        self.wait()

        self.num_disks = original_num_disks
        self.disk_height = original_disk_height

    def move_full_tower(self):
        self.move_subtower_to_peg(self.num_disks, 1, run_time = 2)
        self.wait()
        self.reset_disks(run_time = 1, lag_ratio = 0.5)
        self.wait()

    def move_single_disk(self):
        for x in 0, 1, 0:
            self.move_disk(x)
        self.wait()

    def cannot_move_disk_onto_smaller_disk(self):
        also_not_allowed = OldTexText("Not allowed")
        also_not_allowed.to_edge(UP)
        also_not_allowed.set_color(RED)
        cross = OldTex("\\times")
        cross.set_fill(RED, opacity = 0.5)

        disk = self.disks[2]
        disk.save_state()
        self.move_disks_to_peg([2], 2, added_anims = [
            Transform(self.title, also_not_allowed, run_time = 1)
        ])
        cross.replace(disk)
        self.play(FadeIn(cross))
        self.wait()
        self.play(
            FadeOut(cross),
            FadeOut(self.title),
            disk.restore
        )
        self.wait()

class ExampleFirstMoves(TowersOfHanoiScene):
    def construct(self):
        ruler_sequence = get_ruler_sequence(4)
        cross = OldTex("\\times")
        cross.set_fill(RED, 0.7)

        self.wait()
        self.play(
            self.disks[0].set_fill, YELLOW,
            self.disks[0].label.set_color, BLACK
        )
        self.wait()
        self.move_disk(0)
        self.wait()
        self.play(
            self.disks[1].set_fill, YELLOW_D,
            self.disks[1].label.set_color, BLACK
        )
        self.move_disk_to_peg(1, 1)
        cross.replace(self.disks[1])
        self.play(FadeIn(cross))
        self.wait()
        self.move_disk_to_peg(1, 2, added_anims = [FadeOut(cross)])
        self.wait()
        for x in ruler_sequence[2:9]:
            self.move_disk(x)
        for x in ruler_sequence[9:]:
            self.move_disk(x, run_time = 0.5, stay_on_peg = False)
        self.wait()

class KeithShowingBinary(Scene):
    def construct(self):
        keith = Keith()
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        keith.next_to(morty, LEFT, buff = 2*LARGE_BUFF)
        randy = Randolph()
        randy.next_to(keith, LEFT, buff = 2*LARGE_BUFF)
        randy.bubble = randy.get_bubble(SpeechBubble)
        randy.bubble.set_fill(BLACK, opacity = 1)
        randy.bubble.write("Hold on...how does \\\\ binary work again?")

        binary_tex_mobs = get_binary_tex_mobs(list(range(16)))
        binary_tex_mobs.shift(keith.get_corner(UP+LEFT))
        binary_tex_mobs.shift(0.5*(UP+RIGHT))
        bits_list = binary_tex_mobs.split()
        bits = bits_list.pop(0)

        def get_bit_flip():
            return Transform(
                bits, bits_list.pop(0),
                rate_func = squish_rate_func(smooth, 0, 0.7)
            )

        self.play(
            keith.change_mode, "wave_1",
            keith.look_at, bits,
            morty.look_at, bits,
            Write(bits)
        )
        for x in range(2):
            self.play(get_bit_flip())
        self.play(
            morty.change_mode, "pondering",
            morty.look_at, bits,
            get_bit_flip()
        )
        while bits_list:
            added_anims = []
            if random.random() < 0.2:
                if random.random() < 0.5:
                    added_anims.append(Blink(keith))
                else:
                    added_anims.append(Blink(morty))
            self.play(get_bit_flip(), *added_anims)
        self.wait()
        self.play(
            FadeIn(randy),
            morty.change_mode, "plain",
            morty.look_at, randy.eyes,
            keith.change_mode, "plain",
            keith.look_at, randy.eyes,
        )
        self.play(
            randy.change_mode, "confused",
            ShowCreation(randy.bubble),
            Write(randy.bubble.content)
        )
        self.play(Blink(randy))
        self.wait()
        self.play(morty.change_mode, "hooray")
        self.play(Blink(morty))
        self.wait()

class FocusOnRhythm(Scene):
    def construct(self):
        title = OldTexText("Focus on rhythm")
        title.scale(1.5)
        letters = list(reversed(title[-6:]))
        self.play(Write(title, run_time = 1))
        sequence = get_ruler_sequence(5)
        for x in sequence:
            movers = VGroup(*letters[:x+1])
            self.play(
                movers.shift, 0.2*DOWN,
                rate_func = there_and_back,
                run_time = 0.25
            )

class IntroduceBase10(Scene):
    def construct(self):
        self.expand_example_number()
        self.list_digits()

    def expand_example_number(self):
        title = OldTexText("``Base 10''")
        title.to_edge(UP)
        number = OldTex("137")
        number.next_to(title, DOWN)
        number.shift(2*LEFT)

        colors = [RED, MAROON_B, YELLOW]
        expansion = OldTex(
            "1(100) + ",
            "3(10) + ",
            "7"
        )
        expansion.next_to(number, DOWN, buff = LARGE_BUFF, aligned_edge = RIGHT)        
        arrows = VGroup()
        number.generate_target()

        for color, digit, term in zip(colors, number.target, expansion):
            digit.set_color(color)
            term.set_color(color)
            arrow = Arrow(digit, term.get_top())
            arrow.set_color(color)
            arrows.add(arrow)
        expansion.save_state()
        for digit, term in zip(number, expansion):
            Transform(term, digit).update(1)

        self.play(
            MoveToTarget(number),
            ShowCreation(arrows),
            ApplyMethod(
                expansion.restore, lag_ratio = 0.5),
            run_time = 2
        )
        self.play(Write(title))
        self.wait()
        self.title = title

    def list_digits(self):
        digits = OldTexText("""
            0, 1, 2, 3, 4,
            5, 6, 7, 8, 9
        """)
        digits.next_to(self.title, DOWN, buff = LARGE_BUFF)
        digits.shift(2*RIGHT)
        self.play(Write(digits))
        self.wait()

class RhythmOfDecimalCounting(CountingScene):
    CONFIG = {
        "ones_configuration_location" : 2*UP+2*RIGHT,
        "num_start_location" : DOWN
    }
    def construct(self):
        for x in range(10):
            self.increment()
        brace = Brace(self.number_mob)
        two_digits = brace.get_text("Two digits")
        one_brace = Brace(self.number_mob[-1])
        tens_place = one_brace.get_text("Ten's place")
        ten_group = self.curr_configurations[1][0]

        self.play(
            GrowFromCenter(brace),
            Write(two_digits, run_time = 1)
        )
        self.wait(2)
        self.play(
            Transform(brace, one_brace),
            Transform(two_digits, tens_place)
        )
        self.wait()
        ten_group.save_state()
        self.play(
            ten_group.scale, 7,
            ten_group.shift, 2*(DOWN+LEFT),
        )
        self.wait()
        self.play(
            ten_group.restore,
            *list(map(FadeOut, [brace, two_digits]))
        )

        for x in range(89):
            self.increment(run_time_per_anim = 0.25)
        self.increment(run_time_per_anim = 1)
        self.wait()

        hundred_group = self.curr_configurations[2][0]
        hundred_group.save_state()
        self.play(
            hundred_group.scale, 14,
            hundred_group.to_corner, DOWN+LEFT
        )
        self.wait()
        self.play(hundred_group.restore)
        self.wait()
        groups = [
            VGroup(*pair)
            for pair in zip(self.dot_templates, self.curr_configurations)
        ]
        self.play(
            groups[2].to_edge, RIGHT,
            MaintainPositionRelativeTo(groups[1], groups[2]),
            MaintainPositionRelativeTo(groups[0], groups[2]),
            self.number_mob.to_edge, RIGHT, LARGE_BUFF,
            FadeOut(self.arrows)
        )

class DecimalCountingAtHundredsScale(CountingScene):
    CONFIG = {
        "power_colors" : [RED, GREEN, BLUE, PURPLE_D],
        "counting_dot_starting_position" : (FRAME_X_RADIUS+1)*RIGHT + (FRAME_Y_RADIUS-2)*UP,
        "ones_configuration_location" : 2*UP+5.7*RIGHT,
        "num_start_location" : DOWN + 3*RIGHT
    }
    def construct(self):
        added_zeros = OldTex("00")
        added_zeros.scale(self.num_scale_factor)
        added_zeros.next_to(self.number_mob, RIGHT, SMALL_BUFF, aligned_edge = DOWN)
        added_zeros.set_color_by_gradient(MAROON_B, YELLOW)
        self.add(added_zeros)
        self.increment(run_time_per_anim = 0)

        VGroup(self.number_mob, added_zeros).to_edge(RIGHT, buff = LARGE_BUFF)
        VGroup(self.dot_templates[0], self.curr_configurations[0]).to_edge(RIGHT)
        Transform(
            self.arrows[0], 
            Arrow(self.number_mob, self.dot_templates[0], color = self.power_colors[0])
        ).update(1)

        for x in range(10):
            this_range = list(range(8)) if x == 0 else list(range(9))
            for y in this_range:
                self.increment(run_time_per_anim = 0.25)
            self.increment(run_time_per_anim = 1)

class IntroduceBinaryCounting(BinaryCountingScene):
    CONFIG = {
        "ones_configuration_location" : UP+5*RIGHT,
        "num_start_location" : DOWN+2*RIGHT
    }
    def construct(self):
        self.introduce_name()
        self.initial_counting()
        self.show_self_similarity()

    def introduce_name(self):
        title = OldTexText("Binary (base 2):", "0, 1")
        title.to_edge(UP)
        self.add(title)
        self.number_mob.set_fill(opacity = 0)

        brace = Brace(title[1], buff = SMALL_BUFF)
        bits = OldTexText("bi", "ts", arg_separator = "")
        bits.submobjects.insert(1, VectorizedPoint(bits.get_center()))
        binary_digits = OldTexText("bi", "nary digi", "ts", arg_separator = "")
        for mob in bits, binary_digits:
            mob.next_to(brace, DOWN, buff = SMALL_BUFF)
        VGroup(brace, bits, binary_digits).set_color(BLUE)
        binary_digits[1].set_color(BLUE_E)
        self.play(
            GrowFromCenter(brace),
            Write(bits)
        )
        self.wait()
        bits.save_state()
        self.play(Transform(bits, binary_digits))
        self.wait()
        self.play(bits.restore)
        self.wait()

    def initial_counting(self):
        randy = Randolph().to_corner(DOWN+LEFT)
        bubble = randy.get_bubble(ThoughtBubble, height = 3.4, width = 5)
        bubble.write(
            "Not ten, not ten \\\\",
            "\\quad not ten, not ten..."
        )

        self.play(self.number_mob.set_fill, self.power_colors[0], 1)
        self.increment()
        self.wait()
        self.start_dot = self.curr_configurations[0][0]

        ##Up to 10
        self.increment()
        brace = Brace(self.number_mob[1])
        twos_place = brace.get_text("Two's place")
        self.play(
            GrowFromCenter(brace),
            Write(twos_place)
        )
        self.play(
            FadeIn(randy),
            ShowCreation(bubble)
        )
        self.play(
            randy.change_mode, "hesitant",
            randy.look_at, self.number_mob,
            Write(bubble.content)
        )
        self.wait()
        curr_content = bubble.content
        bubble.write("$1 \\! \\cdot \\! 2+$", "$0$")
        bubble.content[0][0].set_color(self.power_colors[1])
        self.play(
            Transform(curr_content, bubble.content),
            randy.change_mode, "pondering",
            randy.look_at, self.number_mob
        )
        self.remove(curr_content)
        self.add(bubble.content)

        #Up to 11
        zero = bubble.content[-1]
        zero.set_color(self.power_colors[0])
        one = OldTex("1").replace(zero, dim_to_match = 1)
        one.set_color(zero.get_color())
        self.play(Blink(randy))
        self.increment(added_anims = [Transform(zero, one)])
        self.wait()

        #Up to 100
        curr_content = bubble.content
        bubble.write(
            "$1 \\!\\cdot\\! 4 + $",
            "$0 \\!\\cdot\\! 2 + $",
            "$0$",
        )
        colors = reversed(self.power_colors[:3])
        for piece, color in zip(bubble.content.submobjects, colors):
            piece[0].set_color(color)
        self.increment(added_anims = [Transform(curr_content, bubble.content)])
        four_brace = Brace(self.number_mob[-1])
        fours_place = four_brace.get_text("Four's place")
        self.play(
            Transform(brace, four_brace),
            Transform(twos_place, fours_place),
        )
        self.play(Blink(randy))
        self.play(*list(map(FadeOut, [bubble, curr_content])))

        #Up to 1000
        for x in range(4):
            self.increment()
        brace.target = Brace(self.number_mob[-1])
        twos_place.target = brace.get_text("Eight's place")
        self.play(
            randy.change_mode, "happy",
            randy.look_at, self.number_mob,
            *list(map(MoveToTarget, [brace, twos_place]))
        )
        for x in range(8):
            self.increment(total_run_time = 1)
        self.wait()
        for x in range(8):
            self.increment(total_run_time = 1.5)

    def show_self_similarity(self):
        cover_rect = Rectangle()
        cover_rect.set_width(FRAME_WIDTH)
        cover_rect.set_height(FRAME_HEIGHT)
        cover_rect.set_stroke(width = 0)
        cover_rect.set_fill(BLACK, opacity = 0.85)
        big_dot = self.curr_configurations[-1][0].copy()
        self.play(
            FadeIn(cover_rect),
            Animation(big_dot)
        )
        self.play(
            big_dot.center,
            big_dot.set_height, FRAME_HEIGHT-2,
            big_dot.to_edge, LEFT,
            run_time = 5
        )

class BinaryCountingAtEveryScale(Scene):
    CONFIG = {
        "num_bits" : 4,
        "show_title" : False,
    }
    def construct(self):
        title = OldTexText("Count to %d (which is %s in binary)"%(
            2**self.num_bits-1, bin(2**self.num_bits-1)[2:]
        ))
        title.to_edge(UP)
        if self.show_title:
            self.add(title)

        bit_mobs = [
            get_binary_tex_mob(n, self.num_bits)
            for n in range(2**self.num_bits)
        ]
        curr_bits = bit_mobs[0]

        lower_brace = Brace(VGroup(*curr_bits[1:]))
        do_a_thing = lower_brace.get_text("Do a thing")
        VGroup(lower_brace, do_a_thing).set_color(YELLOW)
        upper_brace = Brace(curr_bits, UP)
        roll_over = upper_brace.get_text("Roll over")
        VGroup(upper_brace, roll_over).set_color(MAROON_B)
        again = OldTexText("again")
        again.next_to(do_a_thing, RIGHT, 2*SMALL_BUFF)
        again.set_color(YELLOW)

        self.add(curr_bits, lower_brace, do_a_thing)

        def get_run_through(mobs):
            return Succession(*[
                Transform(
                    curr_bits, mob, 
                    rate_func = squish_rate_func(smooth, 0, 0.5)
                )
                for mob in mobs
            ], run_time = 1)

        for bit_mob in bit_mobs:
            curr_bits.align_data_and_family(bit_mob)
            bit_mob.set_color(YELLOW)
            bit_mob[0].set_color(MAROON_B)
        self.play(get_run_through(bit_mobs[1:2**(self.num_bits-1)]))
        self.play(*list(map(FadeIn, [upper_brace, roll_over])))
        self.play(Transform(
            VGroup(*reversed(list(curr_bits))),
            VGroup(*reversed(list(bit_mobs[2**(self.num_bits-1)]))),
            lag_ratio = 0.5,
        ))
        self.wait()
        self.play(
            get_run_through(bit_mobs[2**(self.num_bits-1)+1:]),
            Write(again)
        )
        self.wait()

class BinaryCountingAtSmallestScale(BinaryCountingAtEveryScale):
    CONFIG = {
        "num_bits" : 2,
        "show_title" : True,
    }

class BinaryCountingAtMediumScale(BinaryCountingAtEveryScale):
    CONFIG = {
        "num_bits" : 4,
        "show_title" : True,
    }

class BinaryCountingAtLargeScale(BinaryCountingAtEveryScale):
    CONFIG = {
        "num_bits" : 8,
        "show_title" : True,
    }

class IntroduceSolveByCounting(TowersOfHanoiScene):
    CONFIG = {
        "num_disks" : 4
    }
    def construct(self):
        self.initialize_bit_mobs()
        for disk in self.disks:
            disk.original_fill_color = disk.get_color()
        braces = [
            Brace(VGroup(*self.curr_bit_mob[:n]))
            for n in range(1, self.num_disks+1)
        ]
        word_list = [
            brace.get_text(text)
            for brace, text in zip(braces, [
                "Only flip last bit",
                "Roll over once",
                "Roll over twice",
                "Roll over three times",
            ])
        ]
        brace = braces[0].copy()
        words = word_list[0].copy()

        ##First increment
        self.play(self.get_increment_animation())
        self.play(
            GrowFromCenter(brace),
            Write(words, run_time = 1)
        )
        disk = self.disks[0]
        last_bit = self.curr_bit_mob[0]
        last_bit.save_state()
        self.play(
            disk.set_fill, YELLOW,
            disk[1].set_fill, BLACK,
            last_bit.set_fill, YELLOW,
        )
        self.wait()
        self.move_disk(0, run_time = 2)
        self.play(
            last_bit.restore,
            disk.set_fill, disk.original_fill_color,
            self.disks[0][1].set_fill, BLACK
        )

        ##Second increment
        self.play(
            self.get_increment_animation(),
            Transform(words, word_list[1]),
            Transform(brace, braces[1]),
        )
        disk = self.disks[1]
        twos_bit = self.curr_bit_mob[1]
        twos_bit.save_state()
        self.play(
            disk.set_fill, MAROON_B,
            disk[1].set_fill, BLACK,
            twos_bit.set_fill, MAROON_B,
        )
        self.move_disk(1, run_time = 2)
        self.wait()
        self.move_disk_to_peg(1, 1, stay_on_peg = False)
        cross = OldTex("\\times")
        cross.replace(disk)
        cross.set_fill(RED, opacity = 0.5)
        self.play(FadeIn(cross))
        self.wait()
        self.move_disk_to_peg(
            1, 2, stay_on_peg = False, 
            added_anims = [FadeOut(cross)]
        )
        self.play(
            disk.set_fill, disk.original_fill_color,
            disk[1].set_fill, BLACK,
            twos_bit.restore,
            Transform(brace, braces[0]),
            Transform(words, word_list[0]),
        )
        self.move_disk(
            0, 
            added_anims = [self.get_increment_animation()],
            run_time = 2
        )
        self.wait()

        ##Fourth increment
        self.play(
            Transform(brace, braces[2]),
            Transform(words, word_list[2]),
        )
        self.play(self.get_increment_animation())
        disk = self.disks[2]
        fours_bit = self.curr_bit_mob[2]
        fours_bit.save_state()
        self.play(
            disk.set_fill, RED,
            disk[1].set_fill, BLACK,
            fours_bit.set_fill, RED
        )
        self.move_disk(2, run_time = 2)
        self.play(
            disk.set_fill, disk.original_fill_color,
            disk[1].set_fill, BLACK,
            fours_bit.restore,
            FadeOut(brace),
            FadeOut(words)
        )
        self.wait()
        for disk_index in 0, 1, 0:
            self.play(self.get_increment_animation())
            self.move_disk(disk_index)
        self.wait()

        ##Eighth incremement
        brace = braces[3]
        words = word_list[3]
        self.play(
            self.get_increment_animation(),
            GrowFromCenter(brace),
            Write(words, run_time = 1)
        )
        disk = self.disks[3]
        eights_bit = self.curr_bit_mob[3]
        eights_bit.save_state()
        self.play(
            disk.set_fill, GREEN,
            disk[1].set_fill, BLACK,
            eights_bit.set_fill, GREEN
        )
        self.move_disk(3, run_time = 2)
        self.play(
            disk.set_fill, disk.original_fill_color,
            disk[1].set_fill, BLACK,
            eights_bit.restore,
        )
        self.play(*list(map(FadeOut, [brace, words])))
        for disk_index in get_ruler_sequence(2):
            self.play(self.get_increment_animation())
            self.move_disk(disk_index, stay_on_peg = False)
        self.wait()

    def initialize_bit_mobs(self):
        bit_mobs = VGroup(*[
            get_binary_tex_mob(n, self.num_disks)
            for n in range(2**(self.num_disks))
        ])
        bit_mobs.scale(2)
        self.bit_mobs_iter = it.cycle(bit_mobs)
        self.curr_bit_mob = next(self.bit_mobs_iter)

        for bit_mob in bit_mobs:
            bit_mob.align_data_and_family(self.curr_bit_mob)
            for bit, disk in zip(bit_mob, reversed(list(self.disks))):
                bit.set_color(disk.get_color())
        bit_mobs.next_to(self.peg_labels, DOWN)

        self.add(self.curr_bit_mob)

    def get_increment_animation(self):
        return Succession(
            Transform(
                self.curr_bit_mob, next(self.bit_mobs_iter),
                lag_ratio = 0.5,
                path_arc = -np.pi/3
            ),
            Animation(self.curr_bit_mob)
        )

class SolveSixDisksByCounting(IntroduceSolveByCounting):
    CONFIG = {
        "num_disks" : 6,
        "stay_on_peg" : False,
        "run_time_per_move" : 0.5,
    }
    def construct(self):
        self.initialize_bit_mobs()
        for disk_index in get_ruler_sequence(self.num_disks-1):
            self.play(
                self.get_increment_animation(),
                run_time = self.run_time_per_move,
            )
            self.move_disk(
                disk_index,
                stay_on_peg = self.stay_on_peg,
                run_time = self.run_time_per_move,
            )
        self.wait()

class RecursionTime(Scene):
    def construct(self):
        keith = Keith().shift(2*DOWN+3*LEFT)
        morty = Mortimer().shift(2*DOWN+3*RIGHT)
        keith.make_eye_contact(morty)

        keith_kick = keith.copy().change_mode("dance_kick")
        keith_kick.scale(1.3)
        keith_kick.shift(0.5*LEFT)
        keith_kick.look_at(morty.eyes)
        keith_hooray = keith.copy().change_mode("hooray")

        self.add(keith, morty)

        bubble = keith.get_bubble(SpeechBubble, height = 2)
        bubble.write("Recursion time!!!")
        VGroup(bubble, bubble.content).shift(UP)

        self.play(
            Transform(keith, keith_kick),
            morty.change_mode, "happy",
            ShowCreation(bubble),
            Write(bubble.content, run_time = 1)
        )
        self.play(
            morty.change_mode, "hooray",
            Transform(keith, keith_hooray),
            bubble.content.set_color_by_gradient, BLUE_A, BLUE_E
        )
        self.play(Blink(morty))
        self.wait()

class RecursiveSolution(TowersOfHanoiScene):
    CONFIG = {
        "num_disks" : 4,
        "middle_peg_bottom" : 2*DOWN,
    }
    def construct(self):
        # VGroup(*self.get_mobjects()).shift(1.5*DOWN)
        big_disk = self.disks[-1]
        self.eyes = Eyes(big_disk)
        title = OldTexText("Move 4-tower")
        sub_steps = OldTexText(
            "Move 3-tower,",
            "Move disk 3,",
            "Move 3-tower",
        )
        sub_steps[1].set_color(GREEN)
        sub_step_brace = Brace(sub_steps, UP)
        sub_sub_steps = OldTexText(
            "Move 2-tower,",
            "Move disk 2,",
            "Move 2-tower",
        )
        sub_sub_steps[1].set_color(RED)
        sub_sub_steps_brace = Brace(sub_sub_steps, UP)
        steps = VGroup(
            title, sub_step_brace, sub_steps, 
            sub_sub_steps_brace, sub_sub_steps
        )
        steps.arrange(DOWN)
        steps.scale(0.7)
        steps.to_edge(UP)
        VGroup(sub_sub_steps_brace, sub_sub_steps).next_to(sub_steps[-1], DOWN)

        self.add(title)

        ##Big disk is frustrated
        self.play(
            FadeIn(self.eyes),
            big_disk.set_fill, GREEN,
            big_disk.label.set_fill, BLACK,
        )
        big_disk.add(self.eyes)        
        self.blink()
        self.wait()
        self.change_mode("angry")
        for x in range(2):
            self.wait()
            self.shake(big_disk)
            self.blink()
            self.wait()
        self.change_mode("plain")
        self.look_at(self.peg_labels[2])
        self.look_at(self.disks[0])
        self.blink()

        #Subtower move
        self.move_subtower_to_peg(3, 1, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[1]),
            FadeIn(sub_step_brace),
            Write(sub_steps[0], run_time = 1)
        ])
        self.wait()
        self.move_disk_to_peg(0, 0, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[0].get_top())
        ])
        self.shake(big_disk)
        self.move_disk_to_peg(0, 2, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[2].get_bottom())
        ])
        self.change_mode("angry")
        self.move_disk_to_peg(0, 1, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.disks[1].get_top())
        ])
        self.blink()

        #Final moves for big case
        self.move_disk(3, run_time = 2, added_anims = [
            Write(sub_steps[1])
        ])
        self.look_at(self.disks[1])
        self.blink()
        bubble = SpeechBubble()
        bubble.write("I'm set!")
        bubble.resize_to_content()
        bubble.pin_to(big_disk)
        bubble.add_content(bubble.content)
        bubble.set_fill(BLACK, opacity = 0.7)
        self.play(
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.wait()
        self.blink()
        self.play(*list(map(FadeOut, [bubble, bubble.content])))
        big_disk.remove(self.eyes)
        self.move_subtower_to_peg(3, 2, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[2].get_top()),
            Write(sub_steps[2])
        ])
        self.play(FadeOut(self.eyes))
        self.wait()

        #Highlight subproblem
        self.play(
            VGroup(*self.disks[:3]).move_to, self.pegs[1], DOWN
        )
        self.disk_tracker = [set([]), set([0, 1, 2]), set([3])]
        arc = Arc(-5*np.pi/6, start_angle = 5*np.pi/6)
        arc.add_tip()
        arc.set_color(YELLOW)
        arc.set_width(
            VGroup(*self.pegs[1:]).get_width()*0.8
        )
        arc.next_to(self.disks[0], UP+RIGHT, buff = SMALL_BUFF)
        q_mark = OldTexText("?")
        q_mark.next_to(arc, UP)
        self.play(
            ShowCreation(arc),
            Write(q_mark),
            sub_steps[-1].set_color, YELLOW
        )
        self.wait()
        self.play(
            GrowFromCenter(sub_sub_steps_brace),
            *list(map(FadeOut, [arc, q_mark]))
        )

        #Disk 2 frustration
        big_disk = self.disks[2]
        self.eyes.move_to(big_disk.get_top(), DOWN)
        self.play(
            FadeIn(self.eyes),
            big_disk.set_fill, RED,
            big_disk.label.set_fill, BLACK
        )
        big_disk.add(self.eyes)
        self.change_mode("sad")
        self.look_at(self.pegs[1].get_top())
        self.shake(big_disk)
        self.blink()

        #Move sub-sub-tower
        self.move_subtower_to_peg(2, 0, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[0].get_bottom()),
            Write(sub_sub_steps[0])
        ])
        self.blink()
        self.move_disk_to_peg(2, 2, run_time = 2, added_anims = [
            Write(sub_sub_steps[1])
        ])
        self.look_at(self.disks[0])
        big_disk.remove(self.eyes)
        self.move_subtower_to_peg(2, 2, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[2].get_top()),
            Write(sub_sub_steps[2])
        ])
        self.blink()
        self.look_at(self.disks[-1])

        #Move eyes
        self.play(FadeOut(self.eyes))
        self.eyes.move_to(self.disks[1].get_top(), DOWN)
        self.play(FadeIn(self.eyes))
        self.blink()
        self.play(FadeOut(self.eyes))
        self.eyes.move_to(self.disks[3].get_top(), DOWN)
        self.play(FadeIn(self.eyes))

        #Show process one last time
        big_disk = self.disks[3]
        big_disk.add(self.eyes)
        self.move_subtower_to_peg(3, 1, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[0])
        ])
        self.move_disk_to_peg(3, 0, run_time = 2)
        big_disk.remove(self.eyes)
        self.move_subtower_to_peg(3, 0, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[0].get_top())
        ])
        self.blink()

    def shake(self, mobject, direction = UP, added_anims = []):
        self.play(
            mobject.shift, 0.2*direction, rate_func = wiggle,
            *added_anims
        )

    def blink(self):
        self.play(self.eyes.blink_anim())

    def look_at(self, point_or_mobject):
        self.play(self.eyes.look_at_anim(point_or_mobject))

    def change_mode(self, mode):
        self.play(self.eyes.change_mode_anim(mode))

class KeithSaysBigToSmall(Scene):
    def construct(self):
        keith = Keith()
        keith.shift(2.5*DOWN + 3*LEFT)
        bubble = keith.get_bubble(SpeechBubble, height = 4.5)
        bubble.write("""
            Big problem
            $\\Downarrow$
            Smaller problem
        """)

        self.add(keith)
        self.play(Blink(keith))
        self.play(
            keith.change_mode, "speaking",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.wait()
        self.play(Blink(keith))
        self.wait()

class CodeThisUp(Scene):
    def construct(self):
        keith = Keith()
        keith.shift(2*DOWN+3*LEFT)
        morty = Mortimer()
        morty.shift(2*DOWN+3*RIGHT)
        keith.make_eye_contact(morty)
        point = 2*UP+3*RIGHT
        bubble = keith.get_bubble(SpeechBubble, width = 4.5, height = 3)
        bubble.write("This is the \\\\ most efficient")
        self.add(morty, keith)

        self.play(
            keith.change_mode, "speaking",
            keith.look_at, point
        )
        self.play(
            morty.change_mode, "pondering",
            morty.look_at, point
        )
        self.play(Blink(keith))
        self.wait(2)
        self.play(Blink(morty))
        self.wait()
        self.play(
            keith.change_mode, "hooray",
            keith.look_at, morty.eyes
        )
        self.play(Blink(keith))
        self.wait()
        self.play(
            keith.change_mode, "speaking",
            keith.look_at, morty.eyes,
            ShowCreation(bubble),
            Write(bubble.content),
            morty.change_mode, "happy",
            morty.look_at, keith.eyes,
        )
        self.wait()
        self.play(Blink(morty))
        self.wait()

class HanoiSolutionCode(Scene):
    def construct(self):
        pass

class NoRoomForInefficiency(Scene):
    def construct(self):
        morty = Mortimer().flip()
        morty.shift(2.5*DOWN+3*LEFT)
        bubble = morty.get_bubble(SpeechBubble, width = 4)
        bubble.write("No room for \\\\ inefficiency")
        VGroup(morty, bubble, bubble.content).to_corner(DOWN+RIGHT)

        self.add(morty)
        self.play(
            morty.change_mode, "speaking",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(morty))
        self.wait()

class WhyDoesBinaryAchieveThis(Scene):
    def construct(self):
        keith = Keith()
        keith.shift(2*DOWN+3*LEFT)
        morty = Mortimer()
        morty.shift(2*DOWN+3*RIGHT)
        keith.make_eye_contact(morty)
        bubble = morty.get_bubble(SpeechBubble, width = 5, height = 3)
        bubble.write("""
            Why does counting
            in binary work?
        """)
        self.add(morty, keith)

        self.play(
            morty.change_mode, "confused",
            morty.look_at, keith.eyes,
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(keith.change_mode, "happy")
        self.wait()
        self.play(Blink(morty))
        self.wait()

class BothAreSelfSimilar(Scene):
    def construct(self):
        morty = Mortimer().flip()
        morty.shift(2.5*DOWN+3*LEFT)
        bubble = morty.get_bubble(SpeechBubble)
        bubble.write("Both are self-similar")

        self.add(morty)
        self.play(
            morty.change_mode, "hooray",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(morty))
        self.wait()

class LargeScaleHanoiDecomposition(TowersOfHanoiScene):
    CONFIG = {
        "num_disks" : 8,
        "peg_height" : 3.5,
        "middle_peg_bottom" : 2*DOWN,
        "disk_max_width" : 4,
    }
    def construct(self):
        self.move_subtower_to_peg(7, 1, stay_on_peg = False)
        self.wait()
        self.move_disk(7, stay_on_peg = False)
        self.wait()
        self.move_subtower_to_peg(7, 2, stay_on_peg = False)
        self.wait()

class SolveTwoDisksByCounting(SolveSixDisksByCounting):
    CONFIG = {
        "num_disks" : 2,
        "stay_on_peg" : False,
        "run_time_per_move" : 1,
        "disk_max_width" : 1.5,
    }
    def construct(self):
        self.initialize_bit_mobs()
        for disk_index in 0, 1, 0:
            self.play(self.get_increment_animation())
            self.move_disk(
                disk_index, 
                stay_on_peg = False,
            )
            self.wait()

class ShowFourDiskFourBitsParallel(IntroduceSolveByCounting):
    CONFIG = {
        "num_disks" : 4,
        "subtask_run_time" : 1,
    }
    def construct(self):
        self.initialize_bit_mobs()
        self.counting_subtask()
        self.wait()
        self.disk_subtask()
        self.wait()
        self.play(self.get_increment_animation())
        self.move_disk(
            self.num_disks-1, 
            stay_on_peg = False,
        )
        self.wait()
        self.counting_subtask()
        self.wait()
        self.disk_subtask()
        self.wait()

    def disk_subtask(self):
        sequence = get_ruler_sequence(self.num_disks-2)
        run_time = float(self.subtask_run_time)/len(sequence)
        for disk_index in get_ruler_sequence(self.num_disks-2):
            self.move_disk(
                disk_index, 
                run_time = run_time,
                stay_on_peg = False,
            )
        # curr_peg = self.disk_index_to_peg_index(0)
        # self.move_subtower_to_peg(self.num_disks-1, curr_peg+1)

    def counting_subtask(self):
        num_tasks = 2**(self.num_disks-1)-1
        run_time = float(self.subtask_run_time)/num_tasks
        # for x in range(num_tasks):
        #     self.play(
        #         self.get_increment_animation(),
        #         run_time = run_time
        #     )
        self.play(
            Succession(*[
                self.get_increment_animation()
                for x in range(num_tasks)
            ]),
            rate_func=linear,
            run_time = self.subtask_run_time
        )

    def get_increment_animation(self):
        return Transform(
            self.curr_bit_mob, next(self.bit_mobs_iter),
            path_arc = -np.pi/3,
        )
 
class ShowThreeDiskThreeBitsParallel(ShowFourDiskFourBitsParallel):
    CONFIG = {
        "num_disks" : 3,
        "subtask_run_time" : 1
    }

class ShowFiveDiskFiveBitsParallel(ShowFourDiskFourBitsParallel):
    CONFIG = {
        "num_disks" : 5,
        "subtask_run_time" : 2
    }

class ShowSixDiskSixBitsParallel(ShowFourDiskFourBitsParallel):
    CONFIG = {
        "num_disks" : 6,
        "subtask_run_time" : 2
    }

class CoolRight(Scene):
    def construct(self):
        morty = Mortimer()
        morty.shift(2*DOWN)
        bubble = SpeechBubble()
        bubble.write("Cool! right?")
        bubble.resize_to_content()
        bubble.pin_to(morty)

        self.play(
            morty.change_mode, "surprised",
            morty.look, OUT,
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(morty))
        self.wait()
        curr_content = bubble.content
        bubble.write("It gets \\\\ better...")
        self.play(
            Transform(curr_content, bubble.content),
            morty.change_mode, "hooray",
            morty.look, OUT
        )
        self.wait()
        self.play(Blink(morty))
        self.wait()

############ Part 2 ############

class MentionLastVideo(Scene):
    def construct(self):
        keith = Keith()
        keith.shift(2*DOWN+3*LEFT)
        morty = Mortimer()
        morty.shift(2*DOWN+3*RIGHT)
        keith.make_eye_contact(morty)
        point = 2*UP

        name = OldTexText("""
            Keith Schwarz
            (Computer Scientist)
        """)
        name.to_corner(UP+LEFT)
        arrow = Arrow(name.get_bottom(), keith.get_top())

        self.add(morty, keith)
        self.play(
            keith.change_mode, "raise_right_hand",
            keith.look_at, point,
            morty.change_mode, "pondering",
            morty.look_at, point
        )
        self.play(Blink(keith))
        self.play(Write(name))
        self.play(ShowCreation(arrow))
        self.play(Blink(morty))
        self.wait(2)
        self.play(
            morty.change_mode, "confused",
            morty.look_at, point
        )
        self.play(Blink(keith))
        self.wait(2)
        self.play(
            morty.change_mode, "surprised"
        )
        self.wait()

class IntroduceConstrainedTowersOfHanoi(ConstrainedTowersOfHanoiScene):
    CONFIG = {
        "middle_peg_bottom" : 2*DOWN,
    }
    def construct(self):
        title = OldTexText("Constrained", "Towers of Hanoi")
        title.set_color_by_tex("Constrained", YELLOW)
        title.to_edge(UP)

        self.play(Write(title))
        self.add_arcs()
        self.disks.save_state()
        for index in 0, 0, 1, 0:
            self.move_disk(index)
            self.wait()
        self.wait()

        self.play(self.disks.restore)
        self.disk_tracker = [set(range(self.num_disks)), set([]), set([])]
        self.wait()
        self.move_disk_to_peg(0, 1)
        self.move_disk_to_peg(1, 2)
        self.play(ShowCreation(self.big_curved_arrow))
        cross = OldTex("\\times")
        cross.scale(2)
        cross.set_fill(RED)
        cross.move_to(self.big_curved_arrow.get_top())
        big_cross = cross.copy()
        big_cross.replace(self.disks[1])
        big_cross.set_fill(opacity = 0.5)
        self.play(FadeIn(cross))
        self.play(FadeIn(big_cross))
        self.wait()


    def add_arcs(self):
        arc = Arc(start_angle = np.pi/6, angle = 2*np.pi/3)
        curved_arrow1 = VGroup(arc, arc.copy().flip())
        curved_arrow2 = curved_arrow1.copy()
        curved_arrows = [curved_arrow1, curved_arrow2]
        for curved_arrow in curved_arrows:
            for arc in curved_arrow:
                arc.add_tip(tip_length = 0.15)
                arc.set_color(YELLOW)
        peg_sets = (self.pegs[:2], self.pegs[1:])
        for curved_arrow, pegs in zip(curved_arrows, peg_sets):
            peg_group = VGroup(*pegs)
            curved_arrow.set_width(0.7*peg_group.get_width())
            curved_arrow.next_to(peg_group, UP)

        self.play(ShowCreation(curved_arrow1))
        self.play(ShowCreation(curved_arrow2))
        self.wait()

        big_curved_arrow = Arc(start_angle = 5*np.pi/6, angle = -2*np.pi/3)
        big_curved_arrow.set_width(0.9*self.pegs.get_width())
        big_curved_arrow.next_to(self.pegs, UP)
        big_curved_arrow.add_tip(tip_length = 0.4)
        big_curved_arrow.set_color(WHITE)
        self.big_curved_arrow = big_curved_arrow

class StillRecruse(Scene):
    def construct(self):
        keith = Keith()
        keith.shift(2*DOWN+3*LEFT)
        morty = Mortimer()
        morty.shift(2*DOWN+3*RIGHT)
        keith.make_eye_contact(morty)
        point = 2*UP+3*RIGHT
        bubble = keith.get_bubble(SpeechBubble, width = 4.5, height = 3)
        bubble.write("You can still\\\\ use recursion")
        self.add(morty, keith)

        self.play(
            keith.change_mode, "speaking",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(morty.change_mode, "hooray")
        self.play(Blink(keith))
        self.wait()
        self.play(Blink(morty))
        self.wait()

class RecursiveSolutionToConstrained(RecursiveSolution):
    CONFIG = {
        "middle_peg_bottom" : 2*DOWN,
        "num_disks" : 4,
    }
    def construct(self):
        big_disk = self.disks[-1]
        self.eyes = Eyes(big_disk)

        #Define steps breakdown text
        title = OldTexText("Move 4-tower")
        subdivisions = [
            OldTexText(
                "\\tiny Move %d-tower,"%d,
                "Move disk %d,"%d,
                "\\, Move %d-tower, \\,"%d,
                "Move disk %d,"%d,
                "Move %d-tower"%d,
            ).set_color_by_tex("Move disk %d,"%d, color)
            for d, color in [(3, GREEN), (2, RED), (1, BLUE_C)]
        ]
        sub_steps, sub_sub_steps = subdivisions[:2]
        for steps in subdivisions:
            steps.set_width(FRAME_WIDTH-1)
        subdivisions.append(
            OldTexText("\\tiny Move disk 0, Move disk 0").set_color(BLUE)
        )
        braces = [
            Brace(steps, UP)
            for steps in subdivisions
        ]
        sub_steps_brace, sub_sub_steps_brace = braces[:2]
        steps = VGroup(title, *it.chain(*list(zip(
            braces, subdivisions
        ))))
        steps.arrange(DOWN)
        steps.to_edge(UP)

        steps_to_fade = VGroup(
            title, sub_steps_brace,
            *list(sub_steps[:2]) + list(sub_steps[3:])
        )
        self.add(title)

        #Initially move big disk
        self.play(
            FadeIn(self.eyes),
            big_disk.set_fill, GREEN,
            big_disk.label.set_fill, BLACK
        )
        big_disk.add(self.eyes)
        big_disk.save_state()
        self.blink()
        self.look_at(self.pegs[2])
        self.move_disk_to_peg(self.num_disks-1, 2, stay_on_peg = False)
        self.look_at(self.pegs[0])
        self.blink()
        self.play(big_disk.restore, path_arc = np.pi/3)
        self.disk_tracker = [set(range(self.num_disks)), set([]), set([])]
        self.look_at(self.pegs[0].get_top())
        self.change_mode("angry")
        self.shake(big_disk)
        self.wait()

        #Talk about tower blocking
        tower = VGroup(*self.disks[:self.num_disks-1])
        blocking = OldTexText("Still\\\\", "Blocking")
        blocking.set_color(RED)
        blocking.to_edge(LEFT)
        blocking.shift(2*UP)
        arrow = Arrow(blocking.get_bottom(), tower.get_top(), buff = SMALL_BUFF)
        new_arrow = Arrow(blocking.get_bottom(), self.pegs[1], buff = SMALL_BUFF)
        VGroup(arrow, new_arrow).set_color(RED)

        self.play(
            Write(blocking[1]),
            ShowCreation(arrow)
        )
        self.shake(tower, RIGHT, added_anims = [Animation(big_disk)])
        self.blink()
        self.shake(big_disk)
        self.wait()
        self.move_subtower_to_peg(self.num_disks-1, 1, added_anims = [
            Transform(arrow, new_arrow),
            self.eyes.look_at_anim(self.pegs[1])
        ])
        self.play(Write(blocking[0]))
        self.shake(big_disk, RIGHT)
        self.wait()
        self.blink()
        self.wait()
        self.play(FadeIn(sub_steps_brace))
        self.move_subtower_to_peg(self.num_disks-1, 2, added_anims = [
            FadeOut(blocking),
            FadeOut(arrow),
            self.eyes.change_mode_anim("plain", thing_to_look_at = self.pegs[2]),
            Write(sub_steps[0], run_time = 1),
        ])
        self.blink()

        #Proceed through actual process
        self.move_disk_to_peg(self.num_disks-1, 1, added_anims = [
            Write(sub_steps[1], run_time = 1),
        ])
        self.wait()
        self.move_subtower_to_peg(self.num_disks-1, 0, added_anims = [
            self.eyes.look_at_anim(self.pegs[0]),
            Write(sub_steps[2], run_time = 1),
        ])
        self.blink()
        self.move_disk_to_peg(self.num_disks-1, 2, added_anims = [
            Write(sub_steps[3], run_time = 1),
        ])
        self.wait()
        big_disk.remove(self.eyes)
        self.move_subtower_to_peg(self.num_disks-1, 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[2].get_top()),
            Write(sub_steps[4], run_time = 1),
        ])
        self.blink()
        self.play(FadeOut(self.eyes))

        #Ask about subproblem
        sub_sub_steps_brace.set_color(WHITE)
        self.move_subtower_to_peg(self.num_disks-1, 0, added_anims = [
            steps_to_fade.fade, 0.7,
            sub_steps[2].set_color, WHITE,
            sub_steps[2].scale, 1.2,
            FadeIn(sub_sub_steps_brace)
        ])
        num_disks = self.num_disks-1
        big_disk = self.disks[num_disks-1]
        self.eyes.move_to(big_disk.get_top(), DOWN)
        self.play(
            FadeIn(self.eyes),
            big_disk.set_fill, RED,
            big_disk.label.set_fill, BLACK,
        )
        big_disk.add(self.eyes)        
        self.blink()

        #Solve subproblem
        self.move_subtower_to_peg(num_disks-1, 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[2]),
            Write(sub_sub_steps[0], run_time = 1)
        ])
        self.blink()
        self.move_disk_to_peg(num_disks-1, 1, added_anims = [
            Write(sub_sub_steps[1], run_time = 1)
        ])
        self.wait()
        self.move_subtower_to_peg(num_disks-1, 0, added_anims = [
            self.eyes.look_at_anim(self.pegs[0]),
            Write(sub_sub_steps[2], run_time = 1)
        ])
        self.blink()
        self.move_disk_to_peg(num_disks-1, 2, added_anims = [
            Write(sub_sub_steps[3], run_time = 1)
        ])
        self.wait()
        big_disk.remove(self.eyes)
        self.move_subtower_to_peg(num_disks-1, 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[2].get_top()),
            Write(sub_sub_steps[4], run_time = 1)
        ])
        self.wait()

        #Show smallest subdivisions
        smaller_subdivision = VGroup(
            *list(subdivisions[2:]) + \
            list(braces[2:])
        )
        last_subdivisions = [VGroup(braces[-1], subdivisions[-1])]
        for vect in LEFT, RIGHT:
            group = last_subdivisions[0].copy()
            group.to_edge(vect)
            steps.add(group)
            smaller_subdivision.add(group)
            last_subdivisions.append(group)
        smaller_subdivision.set_fill(opacity = 0)
        self.play(
            steps.shift, 
            (FRAME_Y_RADIUS-sub_sub_steps.get_top()[1]-MED_SMALL_BUFF)*UP,
            self.eyes.look_at_anim(steps)
        )
        self.play(ApplyMethod(
            VGroup(VGroup(braces[-2], subdivisions[-2])).set_fill, None, 1,
            run_time = 3,
            lag_ratio = 0.5,
        ))
        self.blink()
        for mob in last_subdivisions:
            self.play(
                ApplyMethod(mob.set_fill, None, 1),
                self.eyes.look_at_anim(mob)
            )
        self.blink()
        self.play(FadeOut(self.eyes))
        self.wait()

        #final movements
        movements = [
            (0, 1),
            (0, 0),
            (1, 1),
            (0, 1),
            (0, 2),
            (1, 0),
            (0, 1),
            (0, 0),
        ]
        for disk_index, peg_index in movements:
            self.move_disk_to_peg(
                disk_index, peg_index, 
                stay_on_peg = False
            )
        self.wait()

class SimpleConstrainedBreakdown(TowersOfHanoiScene):
    CONFIG = {
        "num_disks" : 4
    }
    def construct(self):
        self.move_subtower_to_peg(self.num_disks-1, 2)
        self.wait()
        self.move_disk(self.num_disks-1)
        self.wait()
        self.move_subtower_to_peg(self.num_disks-1, 0)
        self.wait()
        self.move_disk(self.num_disks-1)
        self.wait()
        self.move_subtower_to_peg(self.num_disks-1, 2)
        self.wait()

class SolveConstrainedByCounting(ConstrainedTowersOfHanoiScene):
    CONFIG = {
        "num_disks" : 5,
        "ternary_mob_scale_factor" : 2,
    }
    def construct(self):
        ternary_mobs = VGroup()
        for num in range(3**self.num_disks):
            ternary_mob = get_ternary_tex_mob(num, self.num_disks)
            ternary_mob.scale(self.ternary_mob_scale_factor)
            ternary_mob.set_color_by_gradient(*self.disk_start_and_end_colors)
            ternary_mobs.add(ternary_mob)
        ternary_mobs.next_to(self.peg_labels, DOWN)
        self.ternary_mob_iter = it.cycle(ternary_mobs)
        self.curr_ternary_mob = next(self.ternary_mob_iter)
        self.add(self.curr_ternary_mob)

        for index in get_ternary_ruler_sequence(self.num_disks-1):
            self.move_disk(index, stay_on_peg = False, added_anims = [
                self.increment_animation()
            ])

    def increment_animation(self):
        return Succession(
            Transform(
                self.curr_ternary_mob, next(self.ternary_mob_iter),
                lag_ratio = 0.5,
                path_arc = np.pi/6,
            ),
            Animation(self.curr_ternary_mob),
        )

class CompareNumberSystems(Scene):
    def construct(self):
        base_ten = OldTexText("Base ten")
        base_ten.to_corner(UP+LEFT).shift(RIGHT)
        binary = OldTexText("Binary")
        binary.to_corner(UP+RIGHT).shift(LEFT)
        ternary = OldTexText("Ternary")
        ternary.to_edge(UP)
        ternary.set_color(YELLOW)
        titles = [base_ten, binary, ternary]

        zero_to_nine = OldTexText("""
            0, 1, 2, 3, 4,
            5, 6, 7, 8, 9
        """)
        zero_to_nine.next_to(base_ten, DOWN, buff = LARGE_BUFF)
        zero_one = OldTexText("0, 1")
        zero_one.next_to(binary, DOWN, buff = LARGE_BUFF)
        zero_one_two = OldTexText("0, 1, 2")
        zero_one_two.next_to(ternary, DOWN, buff = LARGE_BUFF)
        zero_one_two.set_color_by_gradient(BLUE, GREEN)

        symbols = [zero_to_nine, zero_one, zero_one_two]
        names = ["Digits", "Bits", "Trits?"]
        for mob, text in zip(symbols, names):
            mob.brace = Brace(mob)
            mob.name = mob.brace.get_text(text)
        zero_one_two.name.set_color_by_gradient(BLUE, GREEN)
        dots = OldTex("\\dots")
        dots.next_to(zero_one.name, RIGHT, aligned_edge = DOWN, buff = SMALL_BUFF)

        keith = Keith()
        keith.shift(2*DOWN+3*LEFT)
        keith.look_at(zero_one_two)
        morty = Mortimer()
        morty.shift(2*DOWN+3*RIGHT)

        for title, symbol in zip(titles, symbols):
            self.play(FadeIn(title))
            added_anims = []
            if title is not ternary:
                added_anims += [
                    FadeIn(symbol.brace),
                    FadeIn(symbol.name)
                ]
            self.play(Write(symbol, run_time = 2), *added_anims)
            self.wait()
        self.play(FadeIn(keith))
        self.play(keith.change_mode, "confused")
        self.play(keith.look_at, zero_to_nine)
        self.play(keith.look_at, zero_one)
        self.play(
            GrowFromCenter(zero_one_two.brace),
            Write(zero_one_two.name),
            keith.look_at, zero_one_two,
        )
        self.play(keith.change_mode, "sassy")
        self.play(Blink(keith))
        self.play(FadeIn(morty))
        self.play(
            morty.change_mode, "sassy",
            morty.look_at, zero_one_two
        )
        self.play(Blink(morty))
        self.wait()
        self.play(
            morty.shrug,
            morty.look_at, keith.eyes,
            keith.shrug,
            keith.look_at, morty.eyes
        )
        self.wait()
        self.play(
            morty.change_mode, "hesitant",
            morty.look_at, zero_one.name,
            keith.change_mode, "erm",
            keith.look_at, zero_one.name
        )
        self.play(Blink(morty))
        self.play(Write(dots, run_time = 3))
        self.wait()

class IntroduceTernaryCounting(CountingScene):
    CONFIG = {
        "base" : 3,
        "counting_dot_starting_position" : (FRAME_X_RADIUS-1)*RIGHT + (FRAME_Y_RADIUS-1)*UP,
        "count_dot_starting_radius" : 0.5,
        "dot_configuration_height" : 1,
        "ones_configuration_location" : UP+2*RIGHT,
        "num_scale_factor" : 2,
        "num_start_location" : DOWN+RIGHT,
    }
    def construct(self):
        for x in range(2):
            self.increment()
        self.wait()
        self.increment()
        brace = Brace(self.number_mob[-1])
        threes_place = brace.get_text("Three's place")
        self.play(
            GrowFromCenter(brace),
            Write(threes_place)
        )
        self.wait()
        for x in range(6):
            self.increment()
            self.wait()
        new_brace = Brace(self.number_mob[-1])
        nines_place = new_brace.get_text("Nine's place")
        self.play(
            Transform(brace, new_brace),
            Transform(threes_place, nines_place),
        )
        self.wait()
        for x in range(9):
            self.increment()

class TernaryCountingSelfSimilarPattern(Scene):
    CONFIG = {
        "num_trits" : 3,
        "colors" : CountingScene.CONFIG["power_colors"][:3],
    }
    def construct(self):
        colors = self.colors

        title = OldTexText("Count to " + "2"*self.num_trits)
        for i, color in enumerate(colors):
            title[-i-1].set_color(color)
        steps = VGroup(*list(map(TexText, [
            "Count to %s,"%("2"*(self.num_trits-1)),
            "Roll over,",
            "Count to %s,"%("2"*(self.num_trits-1)),
            "Roll over,",
            "Count to %s,"%("2"*(self.num_trits-1)),
        ])))
        steps.arrange(RIGHT)
        for step in steps[::2]:
            for i, color in enumerate(colors[:-1]):
                step[-i-2].set_color(color)
        VGroup(*steps[1::2]).set_color(colors[-1])
        steps.set_width(FRAME_WIDTH-1)
        brace = Brace(steps, UP)
        word_group = VGroup(title, brace, steps)
        word_group.arrange(DOWN)
        word_group.to_edge(UP)

        ternary_mobs = VGroup(*[
            get_ternary_tex_mob(n, n_trits = self.num_trits)
            for n in range(3**self.num_trits)
        ])
        ternary_mobs.scale(2)
        ternary_mob_iter = it.cycle(ternary_mobs)
        curr_ternary_mob = next(ternary_mob_iter)

        for trits in ternary_mobs:
            trits.align_data_and_family(curr_ternary_mob)
            for trit, color in zip(trits, colors):
                trit.set_color(color)
        def get_increment():
            return Transform(
                curr_ternary_mob, next(ternary_mob_iter),
                lag_ratio = 0.5,
                path_arc = -np.pi/3
            )

        self.add(curr_ternary_mob, title)
        self.play(GrowFromCenter(brace))
        for i, step in enumerate(steps):
            self.play(Write(step, run_time = 1))
            if i%2 == 0:
                self.play(
                    Succession(*[
                        get_increment()
                        for x in range(3**(self.num_trits-1)-1)
                    ]),
                    run_time = 1
                )
            else:
                self.play(get_increment())
            self.wait()

class TernaryCountingSelfSimilarPatternFiveTrits(TernaryCountingSelfSimilarPattern):
    CONFIG = {
        "num_trits" : 5,
        "colors" : color_gradient([YELLOW, PINK, RED], 5),
    }

class CountInTernary(IntroduceTernaryCounting):
    def construct(self):
        for x in range(9):
            self.increment()
        self.wait()

class SolveConstrainedWithTernaryCounting(ConstrainedTowersOfHanoiScene):
    CONFIG = {
        "num_disks" : 4,
    }    
    def construct(self):
        for x in range(3**self.num_disks-1):
            self.increment(run_time = 0.75)
        self.wait()

    def setup(self):
        ConstrainedTowersOfHanoiScene.setup(self)
        ternary_mobs = VGroup(*[
            get_ternary_tex_mob(x)
            for x in range(3**self.num_disks)
        ])
        ternary_mobs.scale(2)
        ternary_mobs.next_to(self.peg_labels, DOWN)

        for trits in ternary_mobs:
            trits.align_data_and_family(ternary_mobs[0])
            trits.set_color_by_gradient(*self.disk_start_and_end_colors)
        self.ternary_mob_iter = it.cycle(ternary_mobs)            
        self.curr_ternary_mob = self.ternary_mob_iter.next().copy()            
        self.disk_index_iter = it.cycle(
            get_ternary_ruler_sequence(self.num_disks-1)
        )
        self.ternary_mobs = ternary_mobs

    def increment(self, run_time = 1, stay_on_peg = False):
        self.increment_number(run_time)
        self.move_next_disk(run_time, stay_on_peg)

    def increment_number(self, run_time = 1):
        self.play(Transform(
            self.curr_ternary_mob, next(self.ternary_mob_iter),
            path_arc = -np.pi/3,
            lag_ratio = 0.5, 
            run_time = run_time,
        ))

    def move_next_disk(self, run_time = None, stay_on_peg = False):
        self.move_disk(
            next(self.disk_index_iter), 
            run_time = run_time,
            stay_on_peg = stay_on_peg
        )

class DescribeSolutionByCountingToConstrained(SolveConstrainedWithTernaryCounting):
    def construct(self):
        braces = [
            Brace(VGroup(*self.curr_ternary_mob[:n+1]))
            for n in range(self.num_disks)
        ]
        words = [
            brace.get_text(text)
            for brace, text in zip(braces, [
                "Only flip last trit",
                "Roll over once",
                "Roll over twice",
                "Roll over three times",
            ])
        ]

        #Count 1, 2
        color = YELLOW
        brace = braces[0]
        word = words[0]
        words[0].set_color(color)
        self.increment_number()        
        self.play(
            FadeIn(brace),
            Write(word, run_time = 1),
            self.curr_ternary_mob[0].set_color, color
        )
        self.wait()
        self.play(
            self.disks[0].set_fill, color,
            self.disks[0].label.set_fill, BLACK,
        )
        self.move_next_disk(stay_on_peg = True)
        self.wait()
        self.ternary_mobs[2][0].set_color(color)
        self.increment_number()
        self.move_next_disk(stay_on_peg = True)
        self.wait()
        
        #Count 10
        color = MAROON_B
        words[1].set_color(color)
        self.increment_number()
        self.play(
            Transform(brace, braces[1]),
            Transform(word, words[1]),
            self.curr_ternary_mob[1].set_color, color
        )
        self.wait()
        self.play(
            self.disks[1].set_fill, color,
            self.disks[1].label.set_fill, BLACK,
        )
        self.move_next_disk(stay_on_peg = True)
        self.wait()
        self.play(*list(map(FadeOut, [brace, word])))

        #Count up to 22
        for x in range(5):
            self.increment()
            self.wait()

        #Count to 100
        color = RED
        words[2].set_color(color)

        self.wait()
        self.increment_number()
        self.play(
            FadeIn(braces[2]),
            Write(words[2], run_time = 1),
            self.curr_ternary_mob[2].set_fill, color,
            self.disks[2].set_fill, color,
            self.disks[2].label.set_fill, BLACK,
        )
        self.wait()
        self.move_next_disk(stay_on_peg = True)
        self.wait()
        self.play(*list(map(FadeOut, [braces[2], words[2]])))

        for x in range(20):
            self.increment()

class Describe2222(Scene):
    def construct(self):
        ternary_mob = OldTex("2222").scale(1.5)
        brace = Brace(ternary_mob)
        description = brace.get_text("$3^4 - 1 = 80$")
        VGroup(ternary_mob, brace, description).scale(1.5)

        self.add(ternary_mob)
        self.wait()
        self.play(GrowFromCenter(brace))
        self.play(Write(description))
        self.wait()

class KeithAsksAboutConfigurations(Scene):
    def construct(self):
        keith = Keith().shift(2*DOWN+3*LEFT)
        morty = Mortimer().shift(2*DOWN+3*RIGHT)
        keith.make_eye_contact(morty)
        bubble = keith.get_bubble(SpeechBubble)
        bubble.write("Think about how many \\\\ configurations there are.")

        self.add(keith, morty)
        self.play(Blink(keith))
        self.play(
            keith.change_mode, "speaking",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(morty))
        self.play(morty.change_mode, "pondering")
        self.wait()

class AskAboutConfigurations(SolveConstrainedWithTernaryCounting):
    def construct(self):
        question = OldTexText("How many configurations?")
        question.scale(1.5)
        question.to_edge(UP)
        self.add(question)

        for x in range(15):
            self.remove(self.curr_ternary_mob)
            self.wait(2)
            for y in range(7):
                self.increment(run_time = 0)

class AnswerConfigurationsCount(TowersOfHanoiScene):
    CONFIG = {
        "middle_peg_bottom" : 2.5*DOWN,
        "num_disks" : 4,
        "peg_height" : 1.5,
    }
    def construct(self):
        answer = OldTexText("$3^4 = 81$ configurations")
        answer.to_edge(UP)
        self.add(answer)

        parentheticals = self.get_parentheticals(answer)

        self.prepare_disks()

        for parens, disk in zip(parentheticals, reversed(list(self.disks))):
            VGroup(parens, parens.brace, parens.three).set_color(disk.get_color())
            self.play(
                Write(parens, run_time = 1),
                FadeIn(disk)
            )
            self.play(
                ApplyMethod(
                    disk.next_to, self.pegs[2], UP,
                    run_time = 2
                ),
                GrowFromCenter(parens.brace),
                Write(parens.three, run_time = 1)
            )
            x_diff = disk.saved_state.get_center()[0]-disk.get_center()[0]
            self.play(
                disk.shift, x_diff*RIGHT
            )
            self.play(disk.restore)
            self.wait()

    def get_parentheticals(self, top_mob):
        parentheticals = VGroup(*reversed([
            OldTex("""
                \\left(
                    \\begin{array}{c}
                        \\text{Choices for} \\\\
                        \\text{disk %d}
                    \\end{array}
                \\right)
            """%d)
            for d in range(self.num_disks)
        ]))
        parentheticals.arrange()
        parentheticals.set_width(FRAME_WIDTH-1)
        parentheticals.next_to(top_mob, DOWN)
        for parens in parentheticals:
            brace = Brace(parens)
            three = brace.get_text("$3$")
            parens.brace = brace
            parens.three = three
        return parentheticals

    def prepare_disks(self):
        configuration = [1, 2, 1, 0]
        for n, peg_index in enumerate(configuration):
            disk_index = self.num_disks-n-1
            disk = self.disks[disk_index]
            top = Circle(radius = disk.get_width()/2)
            inner = Circle(radius = self.peg_width/2)
            inner.flip()
            top.add_subpath(inner.points)
            top.set_stroke(width = 0)
            top.set_fill(disk.get_color())
            top.rotate(np.pi/2, RIGHT)
            top.move_to(disk, UP)
            bottom = top.copy()
            bottom.move_to(disk, DOWN)
            disk.remove(disk.label)
            disk.add(top, bottom, disk.label)
            self.move_disk_to_peg(disk_index, peg_index, run_time = 0)
            if disk_index == 0:
                disk.move_to(self.pegs[peg_index].get_bottom(), DOWN)
        for disk in self.disks:
            disk.save_state()
            disk.rotate(np.pi/30, RIGHT)
            disk.next_to(self.pegs[0], UP)
        self.remove(self.disks)

class ThisIsMostEfficientText(Scene):
    def construct(self):
        text = OldTexText("This is the most efficient solution")
        text.set_width(FRAME_WIDTH - 1)
        text.to_edge(DOWN)
        self.play(Write(text))
        self.wait(2)

class RepeatingConfiguraiton(Scene):
    def construct(self):
        dots = VGroup(*[Dot() for x in range(10)])
        arrows = VGroup(*[Arrow(LEFT, RIGHT) for x in range(9)])
        arrows.add(VGroup())
        arrows.scale(0.5)
        group = VGroup(*it.chain(*list(zip(dots, arrows))))
        group.arrange()
        title = OldTexText("Same state twice")
        title.shift(3*UP)
        special_dots = VGroup(dots[2], dots[6])
        special_arrows = VGroup(*[
            Arrow(title.get_bottom(), dot, color = RED)
            for dot in special_dots
        ])
        mid_mobs = VGroup(*group[5:14])
        mid_arrow = Arrow(dots[2], dots[7], tip_length = 0.125)
        more_efficient = OldTexText("More efficient")
        more_efficient.next_to(mid_arrow, UP)

        self.play(ShowCreation(group, run_time = 2))
        self.play(Write(title))
        self.play(
            ShowCreation(special_arrows),
            special_dots.set_color, RED
        )
        self.wait()
        self.play(
            mid_mobs.shift, 2*DOWN,
            FadeOut(special_arrows)
        )
        self.play(
            ShowCreation(mid_arrow),
            Write(more_efficient)
        )
        self.wait()

class ShowSomeGraph(Scene):
    def construct(self):
        title = OldTexText("Graphs")
        title.scale(2)
        title.to_edge(UP)

        nodes = VGroup(*list(map(Dot, [
            2*LEFT, 
            UP,
            DOWN,
            2*RIGHT,
            2*RIGHT+2*UP,
            2*RIGHT+2*DOWN,
            4*RIGHT+2*UP,
        ])))
        edge_pairs = [
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
            (3, 4),
            (3, 5),
            (4, 6),
        ]
        edges = VGroup()
        for i, j in edge_pairs:
            edges.add(Line(
                nodes[i].get_center(), 
                nodes[j].get_center(), 
            ))

        self.play(Write(title))
        for mob in nodes, edges:
            mob.set_color_by_gradient(YELLOW, MAROON_B)
            self.play(ShowCreation(
                mob, 
                lag_ratio = 0.5,
                run_time = 2,
            ))
        self.wait()

class SierpinskiGraphScene(Scene):
    CONFIG = {
        "num_disks" : 3,
        "towers_config" : {
            "num_disks" : 3,
            "peg_height" : 1.5,
            "peg_spacing" : 2,
            "include_peg_labels" : False,
            "disk_min_width" : 1,
            "disk_max_width" : 2,
        },
        "preliminary_node_radius" : 1,
        "center_to_island_length" : 2.0,
        "include_towers" : True,
        "start_color" : RED,
        "end_color" : GREEN,
        "graph_stroke_width" : 2,
    }
    def setup(self):
        self.initialize_nodes()
        self.add(self.nodes)

        self.initialize_edges()
        self.add(self.edges)

    def initialize_nodes(self):
        circles = self.get_node_circles(self.num_disks)
        circles.set_color_by_gradient(self.start_color, self.end_color)
        circles.set_fill(BLACK, opacity = 0.7)
        circles.set_stroke(width = self.graph_stroke_width)

        self.nodes = VGroup()
        for circle in circles.get_family():
            if not isinstance(circle, Circle):
                continue
            node = VGroup()
            node.add(circle)
            node.circle = circle
            self.nodes.add(node)
        if self.include_towers:
            self.add_towers_to_nodes()
        self.nodes.set_height(FRAME_HEIGHT-2)
        self.nodes.to_edge(UP)

    def get_node_circles(self, order = 3):
        if order == 0:
            return Circle(radius = self.preliminary_node_radius)
        islands = [self.get_node_circles(order-1) for x in range(3)]
        for island, angle in (islands[0], np.pi/6), (islands[2], 5*np.pi/6):
            island.rotate(
                np.pi,
                rotate_vector(RIGHT, angle),
                about_point = island.get_center_of_mass()
            )
        for n, island in enumerate(islands):
            vect = rotate_vector(RIGHT, -5*np.pi/6-n*2*np.pi/3)
            island.scale(0.5)
            island.shift(vect)
        return VGroup(*islands)

    def add_towers_to_nodes(self):
        towers_scene = ConstrainedTowersOfHanoiScene(**self.towers_config)
        tower_scene_group = VGroup(*towers_scene.get_mobjects())
        ruler_sequence = get_ternary_ruler_sequence(self.num_disks-1)
        self.disks = VGroup(*[VGroup() for x in range(self.num_disks)])

        for disk_index, node in zip(ruler_sequence+[0], self.nodes):
            towers = tower_scene_group.copy()
            for mob in towers:
                if hasattr(mob, "label"):
                    self.disks[int(mob.label.tex_string)].add(mob)
            towers.set_width(0.85*node.get_width())
            towers.move_to(node)
            node.towers = towers
            node.add(towers)
            towers_scene.move_disk(disk_index, run_time = 0)            

    def distance_between_nodes(self, i, j):
        return get_norm(
            self.nodes[i].get_center()-\
            self.nodes[j].get_center()
        )

    def initialize_edges(self):
        edges = VGroup()
        self.edge_dict = {}
        min_distance = self.distance_between_nodes(0, 1)
        min_distance *= 1.1 ##Just a little buff to be sure
        node_radius = self.nodes[0].get_width()/2
        for i, j in it.combinations(list(range(3**self.num_disks)), 2):
            center1 = self.nodes[i].get_center()
            center2 = self.nodes[j].get_center()
            vect = center1-center2
            distance = get_norm(center1 - center2)
            if distance < min_distance:
                edge = Line(
                    center1 - (vect/distance)*node_radius,
                    center2 + (vect/distance)*node_radius,
                    color = self.nodes[i].circle.get_stroke_color(),
                    stroke_width = self.graph_stroke_width,
                )
                edges.add(edge)
                self.edge_dict[self.node_indices_to_key(i, j)] = edge
        self.edges = edges

    def node_indices_to_key(self, i, j):
        return ",".join(map(str, sorted([i, j])))

    def node_indices_to_edge(self, i, j):
        key = self.node_indices_to_key(i, j)
        if key not in self.edge_dict:
            warnings.warn("(%d, %d) is not an edge"%(i, j))
            return VGroup()
        return self.edge_dict[key]

    def zoom_into_node(self, node_index, order = 0):
        start_index = node_index - node_index%(3**order)
        node_indices = [start_index + r for r in range(3**order)]
        self.zoom_into_nodes(node_indices)

    def zoom_into_nodes(self, node_indices):
        nodes = VGroup(*[
            self.nodes[index].circle
            for index in node_indices
        ])
        everything = VGroup(*self.get_mobjects())
        if nodes.get_width()/nodes.get_height() > FRAME_X_RADIUS/FRAME_Y_RADIUS:
            scale_factor = (FRAME_WIDTH-2)/nodes.get_width()
        else:
            scale_factor = (FRAME_HEIGHT-2)/nodes.get_height()
        self.play(
            everything.shift, -nodes.get_center(),
            everything.scale, scale_factor
        )
        self.remove(everything)
        self.add(*everything)
        self.wait()

class IntroduceGraphStructure(SierpinskiGraphScene):
    CONFIG = {
        "include_towers" : True, 
        "graph_stroke_width" : 3,
        "num_disks" : 3,
    }
    def construct(self):
        self.remove(self.nodes, self.edges)
        self.introduce_nodes()
        self.define_edges()
        self.tour_structure()

    def introduce_nodes(self):
        self.play(FadeIn(
            self.nodes,
            run_time = 3,
            lag_ratio = 0.5,
        ))
        vect = LEFT
        for index in 3, 21, 8, 17, 10, 13:
            node = self.nodes[index]
            node.save_state()
            self.play(
                node.set_height, FRAME_HEIGHT-2,
                node.next_to, ORIGIN, vect
            )
            self.wait()
            self.play(node.restore)
            node.saved_state = None
            vect = -vect

    def define_edges(self):
        nodes = [self.nodes[i] for i in (12, 14)]
        for node, vect in zip(nodes, [LEFT, RIGHT]):
            node.save_state()
            node.generate_target()
            node.target.set_height(5)
            node.target.center()
            node.target.to_edge(vect)
            arc = Arc(angle = -2*np.pi/3, start_angle = 5*np.pi/6)
            if vect is RIGHT:
                arc.flip()
            arc.set_width(0.8*node.target.towers.get_width())
            arc.next_to(node.target.towers, UP)
            arc.add_tip()
            arc.set_color(YELLOW)
            node.arc = arc

        self.play(*list(map(MoveToTarget, nodes)))
        edge = Line(
            nodes[0].get_right(), nodes[1].get_left(),
            color = YELLOW,
            stroke_width = 6,
        )
        edge.target = self.node_indices_to_edge(12, 14)
        self.play(ShowCreation(edge))
        self.wait()
        for node in nodes:
            self.play(ShowCreation(node.arc))
        self.wait()
        self.play(*[
            FadeOut(node.arc)
            for node in nodes
        ])
        self.play(
            MoveToTarget(edge),
            *[node.restore for node in nodes]
        )
        self.wait()
        self.play(ShowCreation(self.edges, run_time = 3))
        self.wait()

    def tour_structure(self):
        for n in range(3):
            self.zoom_into_node(n)
        self.zoom_into_node(0, 1)
        self.play(
            self.disks[0].set_color, YELLOW,
            *[
                ApplyMethod(disk.label.set_color, BLACK)
                for disk in self.disks[0]
            ]
        )
        self.wait()
        self.zoom_into_node(0, 3)
        self.zoom_into_node(15, 1)
        self.wait()
        self.zoom_into_node(20, 1)
        self.wait()

class DescribeTriforcePattern(SierpinskiGraphScene):
    CONFIG = {
        "index_pairs" : [(7, 1), (2, 3), (5, 6)],
        "scale" : 2,
        "disk_color" : MAROON_B,
        "include_towers" : True,
        "first_connect_0_and_2_islands" : True, #Dumb that I have to do this
    }
    def construct(self):
        index_pair = self.index_pairs[0]
        self.zoom_into_node(index_pair[0], self.scale)
        self.play(
            self.disks[self.scale-1].set_color, self.disk_color,
            *[
                ApplyMethod(disk.label.set_color, BLACK)
                for disk in self.disks[self.scale-1]
            ]
        )

        nodes = [self.nodes[i] for i in index_pair]
        for node, vect in zip(nodes, [LEFT, RIGHT]):
            node.save_state()
            node.generate_target()
            node.target.set_height(6)
            node.target.center().next_to(ORIGIN, vect)

        self.play(*list(map(MoveToTarget, nodes)))
        self.wait()
        self.play(*[node.restore for node in nodes])
        bold_edges = [
            self.node_indices_to_edge(*pair).copy().set_stroke(self.disk_color, 6)
            for pair in self.index_pairs
        ]
        self.play(ShowCreation(bold_edges[0]))
        self.wait()
        self.play(*list(map(ShowCreation, bold_edges[1:])))
        self.wait()

        power_of_three = 3**(self.scale-1)
        index_sets = [
            list(range(0, power_of_three)),
            list(range(power_of_three, 2*power_of_three)),
            list(range(2*power_of_three, 3*power_of_three)),
        ]
        if self.first_connect_0_and_2_islands:
            index_sets = [index_sets[0], index_sets[2], index_sets[1]]
        islands = [
            VGroup(*[self.nodes[i] for i in index_set])
            for index_set in index_sets
        ]
        def wiggle_island(island):
            return ApplyMethod(
                island.rotate, np.pi/12, 
                run_time = 1,
                rate_func = wiggle
            )
        self.play(*list(map(wiggle_island, islands[:2])))
        self.wait()
        self.play(wiggle_island(islands[2]))
        self.wait()
        for index_set in index_sets:
            self.zoom_into_nodes(index_set)
        self.zoom_into_nodes(list(it.chain(*index_sets)))
        self.wait()

class TriforcePatternWord(Scene):
    def construct(self):
        word = OldTexText("Triforce \\\\ pattern")
        word.scale(2)
        word.to_corner(DOWN+RIGHT)
        self.play(Write(word))
        self.wait(2)

class DescribeOrderTwoPattern(DescribeTriforcePattern):
    CONFIG = {
        "index_pairs" : [(8, 9), (17, 18), (4, 22)],
        "scale" : 3,
        "disk_color" : RED,
        "first_connect_0_and_2_islands" : False,
    }

class BiggerTowers(SierpinskiGraphScene):
    CONFIG = {
        "num_disks" : 6,
        "include_towers" : False
    }
    def construct(self):
        for order in range(3, 7):
            self.zoom_into_node(0, order)

class ShowPathThroughGraph(SierpinskiGraphScene):
    CONFIG = {
        "include_towers" : True
    }
    def construct(self):
        arrows = VGroup(*[
            Arrow(
                n1.get_center(),
                n2.get_center(),
                tip_length = 0.15,
                buff = 0.15
            )
            for n1, n2 in zip(self.nodes, self.nodes[1:])
        ])
        self.wait()
        self.play(ShowCreation(
            arrows,
            rate_func=linear,
            run_time = 5
        ))
        self.wait(2)
        for index in range(9):
            self.zoom_into_node(index)

class MentionFinalAnimation(Scene):
    def construct(self):
        morty = Mortimer()
        morty.shift(2*DOWN+3*RIGHT)
        bubble = morty.get_bubble(SpeechBubble, width = 6)
        bubble.write("Before the final\\\\ animation...")

        self.add(morty)
        self.wait()
        self.play(
            morty.change_mode, "speaking",
            morty.look_at, bubble.content,
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(morty))
        self.wait(2)
        self.play(Blink(morty))
        self.wait(2)

class PatreonThanks(Scene):
    CONFIG = {
        "specific_patrons" : [
            "CrypticSwarm",
            "Ali Yahya",
            "Juan    Batiz-Benet",
            "Yu  Jun",
            "Othman  Alikhan",
            "Joseph  John Cox",
            "Luc Ritchie",
            "Einar Johansen",
            "Rish    Kundalia",
            "Achille Brighton",
            "Kirk    Werklund",
            "Ripta   Pasay",
            "Felipe  Diniz",
        ]
    }
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)

        n_patrons = len(self.specific_patrons)
        special_thanks = OldTexText("Special thanks to:")
        special_thanks.set_color(YELLOW)
        special_thanks.shift(3*UP)

        left_patrons = VGroup(*list(map(TexText, 
            self.specific_patrons[:n_patrons/2]
        )))
        right_patrons = VGroup(*list(map(TexText, 
            self.specific_patrons[n_patrons/2:]
        )))
        for patrons, vect in (left_patrons, LEFT), (right_patrons, RIGHT):
            patrons.arrange(DOWN, aligned_edge = LEFT)
            patrons.next_to(special_thanks, DOWN)
            patrons.to_edge(vect, buff = LARGE_BUFF)

        self.play(morty.change_mode, "gracious")
        self.play(Write(special_thanks, run_time = 1))
        self.play(
            Write(left_patrons),
            morty.look_at, left_patrons
        )
        self.play(
            Write(right_patrons),
            morty.look_at, right_patrons
        )
        self.play(Blink(morty))
        for patrons in left_patrons, right_patrons:
            for index in 0, -1:
                self.play(morty.look_at, patrons[index])
                self.wait()

class MortyLookingAtRectangle(Scene):
    def construct(self):
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        url = OldTexText("www.desmos.com/careers")
        url.to_corner(UP+LEFT)
        rect = Rectangle(height = 9, width = 16)
        rect.set_height(5)
        rect.next_to(url, DOWN)
        rect.shift_onto_screen()
        url.save_state()
        url.next_to(morty.get_corner(UP+LEFT), UP)

        self.play(morty.change_mode, "raise_right_hand")
        self.play(Write(url))
        self.play(Blink(morty))
        self.wait()
        self.play(
            url.restore,
            morty.change_mode, "happy"
        )
        self.play(ShowCreation(rect))
        self.wait()
        self.play(Blink(morty))
        self.wait()

class ShowSierpinskiCurvesOfIncreasingOrder(Scene):
    CONFIG = {
        "sierpinski_graph_scene_config" :{
            "include_towers" : False
        },
        "min_order" : 2,
        "max_order" : 7,
        "path_stroke_width" : 7,
    }
    def construct(self):
        graph_scenes = [
            SierpinskiGraphScene(
                num_disks = order,
                **self.sierpinski_graph_scene_config
            )
            for order in range(self.min_order, self.max_order+1)
        ]
        paths = [self.get_path(scene) for scene in graph_scenes]
        graphs = []
        for scene in graph_scenes:
            graphs.append(scene.nodes)
        for graph in graphs:
            graph.set_fill(opacity = 0)

        graph, path = graphs[0], paths[0]

        self.add(graph)
        self.wait()
        self.play(ShowCreation(path, run_time = 3, rate_func=linear))
        self.wait()   
        self.play(graph.fade, 0.5, Animation(path))
        for other_graph in graphs[1:]:
            other_graph.fade(0.5)
        self.wait()
        for new_graph, new_path in zip(graphs[1:], paths[1:]):
            self.play(
                Transform(graph, new_graph),
                Transform(path, new_path),
                run_time = 2
            )
            self.wait()
        self.path = path

    def get_path(self, graph_scene):
        path = VGroup()
        nodes = graph_scene.nodes
        for n1, n2, n3 in zip(nodes, nodes[1:], nodes[2:]):
            segment = VMobject()
            segment.set_points_as_corners([
                n1.get_center(),
                n2.get_center(),
                n3.get_center(),
            ])
            path.add(segment)
        path.set_color_by_gradient(
            graph_scene.start_color,
            graph_scene.end_color,
        )
        path.set_stroke(
            width = self.path_stroke_width - graph_scene.num_disks/2
        )
        return path

class Part1Thumbnail(Scene):
    CONFIG = {
        "part_number" : 1,
        "sierpinski_order" : 5
    }
    def construct(self):
        toh_scene = TowersOfHanoiScene(
            peg_spacing = 2,
            part_number = 1,
        )
        toh_scene.remove(toh_scene.peg_labels)
        toh_scene.pegs[2].set_fill(opacity = 0.5)
        toh = VGroup(*toh_scene.get_mobjects())
        toh.scale(2)
        toh.to_edge(DOWN)
        self.add(toh)

        sierpinski_scene = ShowSierpinskiCurvesOfIncreasingOrder(
            min_order = self.sierpinski_order,
            max_order = self.sierpinski_order,
            skip_animations = True,
        )
        sierpinski_scene.path.set_stroke(width = 10)        
        sierpinski = VGroup(*sierpinski_scene.get_mobjects())
        sierpinski.scale(0.9)
        sierpinski.to_corner(DOWN+RIGHT)
        self.add(sierpinski)

        binary = OldTex("01011")
        binary.set_color_by_tex("0", GREEN)
        binary.set_color_by_tex("1", BLUE)
        binary.set_color_by_gradient(GREEN, RED)
        binary.add_background_rectangle()
        binary.background_rectangle.set_fill(opacity = 0.5)
        # binary.set_fill(opacity = 0.5)
        binary.scale(4)
        binary.to_corner(UP+LEFT)
        self.add(binary)

        part = OldTexText("Part %d"%self.part_number)
        part.scale(4)
        part.to_corner(UP+RIGHT)
        part.add_background_rectangle()
        self.add(part)

class Part2Thumbnail(Part1Thumbnail):
    CONFIG = {
        "part_number" : 2
    }




















# ===== File: ./_2016/patreon.py =====
from manim_imports_ext import *


class SideGigToFullTime(Scene):
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)
        self.add(morty)

        self.side_project(morty)
        self.income(morty)
        self.full_time(morty)

    def side_project(self, morty):
        rect = PictureInPictureFrame()
        rect.next_to(morty, UP+LEFT)
        side_project = OldTexText("Side project")
        side_project.next_to(rect, UP)
        dollar_sign = OldTex("\\$")
        cross = VGroup(*[
            Line(vect, -vect, color = RED)
            for vect in (UP+RIGHT, UP+LEFT)
        ])
        cross.set_height(dollar_sign.get_height())
        no_money = VGroup(dollar_sign, cross)
        no_money.next_to(rect, DOWN)

        self.play(
            morty.change_mode, "raise_right_hand",
            morty.look_at, rect
        )
        self.play(
            Write(side_project),
            ShowCreation(rect)
        )
        self.wait()
        self.play(Blink(morty))
        self.wait()
        self.play(Write(dollar_sign))
        self.play(ShowCreation(cross))

        self.screen_title = side_project
        self.cross = cross

    def income(self, morty):
        dollar_signs = VGroup(*[
            OldTex("\\$")
            for x in range(10)
        ])
        dollar_signs.arrange(RIGHT, buff = LARGE_BUFF)
        dollar_signs.set_color(BLACK)
        dollar_signs.next_to(morty.eyes, RIGHT, buff = 2*LARGE_BUFF)

        self.play(
            morty.change_mode, "happy",
            morty.look_at, dollar_signs, 
            dollar_signs.shift, LEFT,
            dollar_signs.set_color, GREEN
        )
        for x in range(5):
            last_sign = dollar_signs[0]
            dollar_signs.remove(last_sign)
            self.play(
                FadeOut(last_sign),
                dollar_signs.shift, LEFT
            )
        random.shuffle(dollar_signs.submobjects)
        self.play(
            ApplyMethod(
                dollar_signs.shift, 
                (FRAME_Y_RADIUS+1)*DOWN,
                lag_ratio = 0.5
            ),
            morty.change_mode, "guilty",
            morty.look, DOWN+RIGHT
        )
        self.play(Blink(morty))

    def full_time(self, morty):
        new_title = OldTexText("Full time")
        new_title.move_to(self.screen_title)
        q_mark = OldTex("?")
        q_mark.next_to(self.cross)
        q_mark.set_color(GREEN)

        self.play(morty.look_at, q_mark)
        self.play(Transform(self.screen_title, new_title))
        self.play(
            Transform(self.cross, q_mark),
            morty.change_mode, "confused"
        )
        self.play(Blink(morty))
        self.wait()
        self.play(
            morty.change_mode, "happy",
            morty.look, UP+RIGHT
        )
        self.play(Blink(morty))
        self.wait()

class TakesTime(Scene):
    def construct(self):
        rect = PictureInPictureFrame(height = 4)
        rect.to_edge(RIGHT, buff = LARGE_BUFF)
        clock = Clock()
        clock.hour_hand.set_color(BLUE_C)
        clock.minute_hand.set_color(BLUE_D)
        clock.next_to(rect, LEFT, buff = LARGE_BUFF)
        self.add(rect)
        self.play(ShowCreation(clock))
        for x in range(3):
            self.play(ClockPassesTime(clock))

class GrowingToDoList(Scene):
    def construct(self):
        morty = Mortimer()
        morty.flip()
        morty.next_to(ORIGIN, DOWN+LEFT)
        title = OldTexText("3blue1brown to-do list")
        title.next_to(ORIGIN, RIGHT)
        title.to_edge(UP)
        underline = Line(title.get_left(), title.get_right())
        underline.next_to(title, DOWN)

        lines = VGroup(*list(map(TexText, [
            "That one on topology",
            "Something with quaternions",
            "Solving puzzles with binary counting",
            "Tatoos on math",
            "Laplace stuffs",
            "The role of memorization in math",
            "Strangeness of the axiom of choice",
            "Tensors",
            "Different view of $e^{\\pi i}$",
            "Quadratic reciprocity",
            "Fourier stuffs",
            "$1+2+3+\\cdots = -\\frac{1}{12}$",
            "Understanding entropy",
        ])))
        lines.scale(0.65)
        lines.arrange(DOWN, buff = MED_SMALL_BUFF, aligned_edge = LEFT)
        lines.set_color_by_gradient(BLUE_C, YELLOW)
        lines.next_to(title, DOWN, buff = LARGE_BUFF/2.)
        lines.to_edge(RIGHT)

        self.play(
            Write(title),
            morty.look_at, title
        )
        self.play(
            Write(lines[0]), 
            morty.change_mode, "erm",
            run_time = 1
        )
        for line in lines[1:3]:
            self.play(
                Write(line), 
                morty.look_at, line,
                run_time = 1
            )
        self.play(
            morty.change_mode, "pleading",
            morty.look_at, lines,
            Write(
                VGroup(*lines[3:]),
            )
        )

class TwoTypesOfVideos(Scene):
    def construct(self):
        morty = Mortimer().shift(2*DOWN)
        stand_alone = OldTexText("Standalone videos")
        stand_alone.shift(FRAME_X_RADIUS*LEFT/2)
        stand_alone.to_edge(UP)
        series = OldTexText("Series")
        series.shift(FRAME_X_RADIUS*RIGHT/2)
        series.to_edge(UP)
        box = Rectangle(width = 16, height = 9, color = WHITE)
        box.set_height(3)
        box.next_to(stand_alone, DOWN)
        series_list = VGroup(*[  
            OldTexText("Essence of %s"%s)
            for s in [
                "linear algebra",
                "calculus",
                "probability",
                "real analysis",
                "complex analysis",
                "ODEs",
            ]
        ])
        series_list.arrange(DOWN, aligned_edge = LEFT, buff = MED_SMALL_BUFF)
        series_list.set_width(FRAME_X_RADIUS-2)
        series_list.next_to(series, DOWN, buff = MED_SMALL_BUFF)
        series_list.to_edge(RIGHT)

        fridays = OldTexText("Every other friday")
        when_done = OldTexText("When series is done")
        for words, vect in (fridays, LEFT), (when_done, RIGHT):
            words.set_color(YELLOW)
            words.next_to(
                morty, vect, 
                buff = MED_SMALL_BUFF, 
                aligned_edge = UP
            )
        unless = OldTexText("""
            Unless you're
            a patron \\dots
        """)
        unless.next_to(when_done, DOWN, buff = MED_SMALL_BUFF)

        self.add(morty)
        self.play(Blink(morty))
        self.play(
            morty.change_mode, "raise_right_hand",
            morty.look_at, stand_alone,
            Write(stand_alone, run_time = 2),
        )
        self.play(
            morty.change_mode, "raise_left_hand",
            morty.look_at, series,
            Write(series, run_time = 2),
        )
        self.play(Blink(morty))
        self.wait()
        self.play(
            morty.change_mode, "raise_right_hand",
            morty.look_at, box,
            ShowCreation(box)
        )
        for x in range(3):
            self.wait(2)
            self.play(Blink(morty))            
        self.play(
            morty.change_mode, "raise_left_hand",
            morty.look_at, series
        )
        for i, words in enumerate(series_list):
            self.play(Write(words), run_time = 1)
        self.play(Blink(morty))
        self.wait()
        self.play(series_list[1].set_color, BLUE)
        self.wait(2)
        self.play(Blink(morty))
        self.wait()
        pairs = [
            (fridays, "speaking"), 
            (when_done, "wave_2") ,
            (unless, "surprised"),
        ]
        for words, mode in pairs:
            self.play(
                Write(words),
                morty.change_mode, mode,
                morty.look_at, words
            )
            self.wait()

class ClassWatching(TeacherStudentsScene):
    def construct(self):
        rect = PictureInPictureFrame(height = 4)
        rect.next_to(self.get_teacher(), UP, buff = LARGE_BUFF/2.)
        rect.to_edge(RIGHT)
        self.add(rect)
        for pi in self.get_students():
            pi.look_at(rect)

        self.random_blink(5)
        self.play_student_changes(
            "raise_left_hand",
            "raise_right_hand",            
            "sassy",
        )
        self.play(self.get_teacher().change_mode, "pondering")
        self.random_blink(3)

class RandolphWatching(Scene):
    def construct(self):
        randy = Randolph()
        randy.shift(2*LEFT)
        randy.look(RIGHT)

        self.add(randy)
        self.wait()
        self.play(Blink(randy))
        self.wait()
        self.play(
            randy.change_mode, "pondering",
            randy.look, RIGHT
        )
        self.play(Blink(randy))
        self.wait()

class RandolphWatchingWithLaptop(Scene):
    pass

class GrowRonaksSierpinski(Scene):
    CONFIG = {
        "colors" : [BLUE, YELLOW, BLUE_C, BLUE_E],
        "dot_radius" : 0.08,
        "n_layers" : 64,
    }
    def construct(self):
        sierp = self.get_ronaks_sierpinski(self.n_layers)
        dots = self.get_dots(self.n_layers)
        self.triangle = VGroup(sierp, dots)
        self.triangle.scale(1.5)
        self.triangle.shift(3*UP)
        sierp_layers = sierp.submobjects
        dot_layers = dots.submobjects

        last_dot_layer = dot_layers[0]
        self.play(ShowCreation(last_dot_layer))
        run_time = 1
        for n, sierp_layer, dot_layer in zip(it.count(1), sierp_layers, dot_layers[1:]):
            self.play(
                ShowCreation(sierp_layer, lag_ratio=1),
                Animation(last_dot_layer),
                run_time = run_time
            )
            self.play(ShowCreation(
                dot_layer,
                run_time = run_time,
                lag_ratio=1,
            ))
            # if n == 2:
            #     dot = dot_layer[1]
            #     words = OldTexText("Stop growth at pink")
            #     words.next_to(dot, DOWN, 2)
            #     arrow = Arrow(words, dot)
            #     self.play(
            #         Write(words),
            #         ShowCreation(arrow)
            #     )
            #     self.wait()
            #     self.play(*map(FadeOut, [words, arrow]))
            log2 = np.log2(n)
            if n > 2 and log2-np.round(log2) == 0 and n < self.n_layers:
                self.wait()
                self.rescale()
                run_time /= 1.3
            last_dot_layer = dot_layer

    def rescale(self):
        shown_mobs = VGroup(*self.get_mobjects())
        shown_mobs_copy = shown_mobs.copy()
        self.remove(shown_mobs)
        self.add(shown_mobs_copy)
        top = shown_mobs.get_top()
        self.triangle.scale(0.5)
        self.triangle.move_to(top, aligned_edge = UP)
        self.play(Transform(shown_mobs_copy, shown_mobs))
        self.remove(shown_mobs_copy)
        self.add(shown_mobs)

    def get_pascal_point(self, n, k):
        return n*rotate_vector(RIGHT, -2*np.pi/3) + k*RIGHT

    def get_lines_at_layer(self, n):
        lines = VGroup()
        for k in range(n+1):
            if choose(n, k)%2 == 1:
                p1 = self.get_pascal_point(n, k)
                p2 = self.get_pascal_point(n+1, k)
                p3 = self.get_pascal_point(n+1, k+1)
                lines.add(Line(p1, p2), Line(p1, p3))
        return lines

    def get_dot_layer(self, n):
        dots = VGroup()
        for k in range(n+1):
            p = self.get_pascal_point(n, k)
            dot = Dot(p, radius = self.dot_radius)
            if choose(n, k)%2 == 0:
                if choose(n-1, k)%2 == 0:
                    continue
                dot.set_color(PINK)
            else:
                dot.set_color(WHITE)
            dots.add(dot)
        return dots

    def get_ronaks_sierpinski(self, n_layers):
        ronaks_sierpinski = VGroup()
        for n in range(n_layers):
            ronaks_sierpinski.add(self.get_lines_at_layer(n))
        ronaks_sierpinski.set_color_by_gradient(*self.colors)
        ronaks_sierpinski.set_stroke(width = 0)##TODO
        return ronaks_sierpinski

    def get_dots(self, n_layers):
        dots = VGroup()        
        for n in range(n_layers+1):
            dots.add(self.get_dot_layer(n))
        return dots

class PatreonLogo(Scene):
    def construct(self):
        words1 = OldTexText(
            "Support future\\\\",
            "3blue1brown videos"
        )
        words2 = OldTexText(
            "Early access to\\\\",
            "``Essence of'' series"
        )
        for words in words1, words2:
            words.scale(2)
            words.to_edge(DOWN)
        self.play(Write(words1))
        self.wait(2)
        self.play(Transform(words1, words2))
        self.wait(2)

class PatreonLogin(Scene):
    pass

class PythagoreanTransformation(Scene):
    def construct(self):
        tri1 = VGroup(
            Line(ORIGIN, 2*RIGHT, color = BLUE),
            Line(2*RIGHT, 3*UP, color = YELLOW),
            Line(3*UP, ORIGIN, color = MAROON_B),
        )
        tri1.shift(2.5*(DOWN+LEFT))
        tri2, tri3, tri4 = copies = [
            tri1.copy().rotate(-i*np.pi/2)
            for i in range(1, 4)
        ]
        a = OldTex("a").next_to(tri1[0], DOWN, buff = MED_SMALL_BUFF)
        b = OldTex("b").next_to(tri1[2], LEFT, buff = MED_SMALL_BUFF)
        c = OldTex("c").next_to(tri1[1].get_center(), UP+RIGHT)

        c_square = Polygon(*[
            tri[1].get_end()
            for tri in [tri1] + copies
        ])
        c_square.set_stroke(width = 0)
        c_square.set_fill(color = YELLOW, opacity = 0.5)
        c_square_tex = OldTex("c^2")
        big_square = Polygon(*[
            tri[0].get_start()
            for tri in [tri1] + copies
        ])
        big_square.set_color(WHITE)
        a_square = Square(side_length = 2)
        a_square.shift(1.5*(LEFT+UP))
        a_square.set_stroke(width = 0)
        a_square.set_fill(color = BLUE, opacity = 0.5)
        a_square_tex = OldTex("a^2")
        a_square_tex.move_to(a_square)
        b_square = Square(side_length = 3)
        b_square.move_to(
            a_square.get_corner(DOWN+RIGHT),
            aligned_edge = UP+LEFT
        )
        b_square.set_stroke(width = 0)
        b_square.set_fill(color = MAROON_B, opacity = 0.5)
        b_square_tex = OldTex("b^2")
        b_square_tex.move_to(b_square)

        self.play(ShowCreation(tri1, run_time = 2))
        self.play(*list(map(Write, [a, b, c])))
        self.wait()
        self.play(
            FadeIn(c_square),
            Animation(c)
        )
        self.play(Transform(c, c_square_tex))
        self.wait(2)
        mover = tri1.copy()
        for copy in copies:
            self.play(Transform(
                mover, copy,
                path_arc = -np.pi/2
            ))
            self.add(copy)
        self.remove(mover)
        self.add(big_square, *[tri1]+copies)
        self.wait(2)
        self.play(*list(map(FadeOut, [a, b, c, c_square])))
        self.play(
            tri3.shift,
            tri1.get_corner(UP+LEFT) -\
            tri3.get_corner(UP+LEFT)
        )
        self.play(tri2.shift, 2*RIGHT)
        self.play(tri4.shift, 3*UP)
        self.wait()
        self.play(FadeIn(a_square))
        self.play(FadeIn(b_square))
        self.play(Write(a_square_tex))
        self.play(Write(b_square_tex))
        self.wait(2)

class KindWordsOnEoLA(TeacherStudentsScene):
    def construct(self):
        rect = Rectangle(width = 16, height = 9, color = WHITE)
        rect.set_height(4)
        title = OldTexText("Essence of linear algebra")
        title.to_edge(UP)
        rect.next_to(title, DOWN)
        self.play(
            Write(title), 
            ShowCreation(rect),
            *[
                ApplyMethod(pi.look_at, rect)
                for pi in self.get_pi_creatures()
            ],
            run_time = 2
        )
        self.random_blink()
        self.play_student_changes(*["hooray"]*3)
        self.random_blink()
        self.play(self.get_teacher().change_mode, "happy")
        self.random_blink()

class MakeALotOfPiCreaturesHappy(Scene):
    def construct(self):
        width = 7
        height = 4
        pis = VGroup(*[
            VGroup(*[
                Randolph()
                for x in range(7)
            ]).arrange(RIGHT, buff = MED_LARGE_BUFF)
            for x in range(4)
        ]).arrange(DOWN, buff = MED_LARGE_BUFF)

        pi_list = list(it.chain(*[
            layer.submobjects
            for layer in pis.submobjects
        ]))
        random.shuffle(pi_list)
        colors = color_gradient([BLUE_D, GREY_BROWN], len(pi_list))
        for pi, color in zip(pi_list, colors):
            pi.set_color(color)
        pis = VGroup(*pi_list)
        pis.set_height(6)

        self.add(pis)
        pis.generate_target()
        self.wait()
        for pi, color in zip(pis.target, colors):
            pi.change_mode("hooray")
            # pi.scale(1)
            pi.set_color(color)
        self.play(
            MoveToTarget(
                pis,
                run_time = 2,
                lag_ratio = 0.5,
            )
        )
        for x in range(10):
            pi = random.choice(pi_list)
            self.play(Blink(pi))


class IntegrationByParts(Scene):
    def construct(self):
        rect = Rectangle(width = 5, height = 3)
        # f = lambda t : 4*np.sin(t*np.pi/2)
        f = lambda t : 4*t
        g = lambda t : 3*smooth(t)
        curve = ParametricCurve(lambda t : f(t)*RIGHT + g(t)*DOWN)
        curve.set_color(YELLOW)
        curve.center()
        rect = Rectangle()
        rect.replace(curve, stretch = True)

        regions = []
        for vect, color in (UP+RIGHT, BLUE), (DOWN+LEFT, GREEN):
            region = curve.copy()
            region.add_line_to(rect.get_corner(vect))
            region.set_stroke(width = 0)
            region.set_fill(color = color, opacity = 0.5)
            regions.append(region)
        upper_right, lower_left = regions

        v_lines, h_lines = VGroup(), VGroup()
        for alpha in np.linspace(0, 1, 30):
            point = curve.point_from_proportion(alpha)
            top_point = curve.get_points()[0][1]*UP + point[0]*RIGHT
            left_point = curve.get_points()[0][0]*RIGHT + point[1]*UP
            v_lines.add(Line(top_point, point))
            h_lines.add(Line(left_point, point))
        v_lines.set_color(BLUE_E)
        h_lines.set_color(GREEN_E)

        equation = OldTex(
            "\\int_0^1 g\\,df", 
            "+\\int_0^1 f\\,dg",
            "= \\big(fg \\big)_0^1"
        )
        equation.to_edge(UP)
        equation.set_color_by_tex(
            "\\int_0^1 g\\,df",
            upper_right.get_color()
        )
        equation.set_color_by_tex(
            "+\\int_0^1 f\\,dg",
            lower_left.get_color()
        )

        left_brace = Brace(rect, LEFT)
        down_brace = Brace(rect, DOWN)
        g_T = left_brace.get_text("$g(t)\\big|_0^1$")
        f_T = down_brace.get_text("$f(t)\\big|_0^1$")

        self.draw_curve(curve)
        self.play(ShowCreation(rect))
        self.play(*list(map(Write, [down_brace, left_brace, f_T, g_T])))
        self.wait()
        self.play(FadeIn(upper_right))
        self.play(
            ShowCreation(
                v_lines,
                run_time = 2
            ),
            Animation(curve),
            Animation(rect)
        )
        self.play(Write(equation[0]))
        self.wait()
        self.play(FadeIn(lower_left))
        self.play(
            ShowCreation(
                h_lines,
                run_time = 2
            ),
            Animation(curve),
            Animation(rect)
        )
        self.play(Write(equation[1]))
        self.wait()
        self.play(Write(equation[2]))
        self.wait()

    def draw_curve(self, curve):
        lp, lnum, comma, rnum, rp = coords = OldTex(
            "\\big(f(", "t", "), g(", "t", ")\\big)"
        )
        coords.set_color_by_tex("0.00", BLACK)
        dot = Dot(radius = 0.1)
        dot.move_to(curve.get_points()[0])
        coords.next_to(dot, UP+RIGHT)
        self.play(
            ShowCreation(curve),
            UpdateFromFunc(
                dot,
                lambda d : d.move_to(curve.get_points()[-1])
            ),
            MaintainPositionRelativeTo(coords, dot),
            run_time = 5,
            rate_func=linear
        )
        self.wait()
        self.play(*list(map(FadeOut, [coords, dot])))

class EndScreen(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            """
            See you every 
            other friday!
            """,
            target_mode = "hooray"
        )
        self.play_student_changes(*["happy"]*3)
        self.random_blink()

































# ===== File: ./_2016/wcat.py =====
from manim_imports_ext import *


class ClosedLoopScene(Scene):
    CONFIG = {
        "loop_anchor_points" : [
            3*RIGHT,
            2*RIGHT+UP,
            3*RIGHT + 3*UP,
            UP,
            2*UP+LEFT,
            2*LEFT + 2*UP,
            3*LEFT,
            2*LEFT+DOWN,
            3*LEFT+2*DOWN,
            2*DOWN+RIGHT,
            LEFT+DOWN,
        ],
        "square_vertices" : [
            2*RIGHT+UP,
            2*UP+LEFT,
            2*LEFT+DOWN,
            2*DOWN+RIGHT
        ],
        "rect_vertices" : [
            0*RIGHT + 1*UP,
            -1*RIGHT +  2*UP,
            -3*RIGHT +  0*UP,
            -2*RIGHT + -1*UP,
        ],
        "dot_color" : YELLOW,
        "connecting_lines_color" : BLUE,
        "pair_colors" : [MAROON_B, PURPLE_B],
    }
    def setup(self):
        self.dots = VGroup()
        self.connecting_lines = VGroup()
        self.add_loop()

    def add_loop(self):
        self.loop = self.get_default_loop()
        self.add(self.loop)

    def get_default_loop(self):
        loop = VMobject()
        loop.set_points_smoothly(
            self.loop_anchor_points + [self.loop_anchor_points[0]]
        )
        return loop

    def get_square(self):
        return Polygon(*self.square_vertices)

    def get_rect_vertex_dots(self, square = False):
        if square:
            vertices = self.square_vertices
        else:
            vertices = self.rect_vertices
        dots = VGroup(*[Dot(v) for v in vertices])
        dots.set_color(self.dot_color)
        return dots

    def get_rect_alphas(self, square = False):
        #Inefficient and silly, but whatever.
        dots = self.get_rect_vertex_dots(square = square)
        return self.get_dot_alphas(dots)

    def add_dot(self, dot):
        self.add_dots(dot)

    def add_dots(self, *dots):
        self.dots.add(*dots)
        self.add(self.dots)

    def add_rect_dots(self, square = False):
        self.add_dots(*self.get_rect_vertex_dots(square = square))

    def add_dots_at_alphas(self, *alphas):
        self.add_dots(*[
            Dot(
                self.loop.point_from_proportion(alpha), 
                color = self.dot_color
            )
            for alpha in alphas
        ])

    def add_connecting_lines(self, cyclic = False):
        if cyclic:
            pairs = adjacent_pairs(self.dots)
        else:
            n_pairs = len(list(self.dots))/2
            pairs = list(zip(self.dots[:n_pairs], self.dots[n_pairs:]))
        for d1, d2 in pairs:
            line = Line(d1.get_center(), d2.get_center())
            line.start_dot = d1 
            line.end_dot = d2
            line.update_anim = UpdateFromFunc(
                line,
                lambda l : l.put_start_and_end_on(
                    l.start_dot.get_center(),
                    l.end_dot.get_center()
                )
            )
            line.set_color(d1.get_color())
            self.connecting_lines.add(line)
        if cyclic:
            self.connecting_lines.set_color(self.connecting_lines_color)
            self.connecting_lines.set_stroke(width = 6)
        self.add(self.connecting_lines, self.dots)

    def get_line_anims(self):
        return [
            line.update_anim
            for line in self.connecting_lines
        ] + [Animation(self.dots)]

    def get_dot_alphas(self, dots = None, precision = 0.005):
        if dots == None:
            dots = self.dots
        alphas = []
        alpha_range = np.arange(0, 1, precision)
        loop_points = np.array(list(map(self.loop.point_from_proportion, alpha_range)))
        for dot in dots:
            vects = loop_points - dot.get_center()
            norms = np.apply_along_axis(get_norm, 1, vects)
            index = np.argmin(norms)
            alphas.append(alpha_range[index])
        return alphas

    def let_dots_wonder(self, run_time = 5, random_seed = None, added_anims = []):
        if random_seed is not None:
            np.random.seed(random_seed)
        start_alphas = self.get_dot_alphas()
        alpha_rates = 0.05 + 0.1*np.random.random(len(list(self.dots)))
        def generate_rate_func(start, rate):
            return lambda t : (start + t*rate*run_time)%1
        anims = [
            MoveAlongPath(
                dot,
                self.loop,
                rate_func = generate_rate_func(start, rate)
            )
            for dot, start, rate in zip(self.dots, start_alphas, alpha_rates)
        ]
        anims += self.get_line_anims()
        anims += added_anims
        self.play(*anims, run_time = run_time)

    def move_dots_to_alphas(self, alphas, run_time = 3):
        assert(len(alphas) == len(list(self.dots)))
        start_alphas = self.get_dot_alphas()
        def generate_rate_func(start_alpha, alpha):
            return lambda t : interpolate(start_alpha, alpha, smooth(t))
        anims = [
            MoveAlongPath(
                dot, self.loop,
                rate_func = generate_rate_func(sa, a),
                run_time = run_time,
            )
            for dot, sa, a in zip(self.dots, start_alphas, alphas)
        ]
        anims += self.get_line_anims()
        self.play(*anims)

    def transform_loop(self, target_loop, added_anims = [], **kwargs):
        alphas = self.get_dot_alphas()
        dot_anims = []
        for dot, alpha in zip(self.dots, alphas):
            dot.generate_target()
            dot.target.move_to(target_loop.point_from_proportion(alpha))
            dot_anims.append(MoveToTarget(dot))
        self.play(
            Transform(self.loop, target_loop),
            *dot_anims + self.get_line_anims() + added_anims,
            **kwargs
        )

    def set_color_dots_by_pair(self):
        n_pairs = len(list(self.dots))/2
        for d1, d2, c in zip(self.dots[:n_pairs], self.dots[n_pairs:], self.pair_colors):
            VGroup(d1, d2).set_color(c)

    def find_square(self):
        alpha_quads = list(it.combinations(
            np.arange(0, 1, 0.02) , 4
        ))
        quads = np.array([
            [
                self.loop.point_from_proportion(alpha)
                for alpha in quad
            ]
            for quad in alpha_quads
        ])
        scores = self.square_scores(quads)
        index = np.argmin(scores)
        return quads[index]

    def square_scores(self, all_quads):
        midpoint_diffs = np.apply_along_axis(
            get_norm, 1,
            0.5*(all_quads[:,0] + all_quads[:,2]) - 0.5*(all_quads[:,1] + all_quads[:,3])
        )
        vects1 = all_quads[:,0] - all_quads[:,2]
        vects2 = all_quads[:,1] - all_quads[:,3]
        distances1 = np.apply_along_axis(get_norm, 1, vects1)
        distances2 = np.apply_along_axis(get_norm, 1, vects2)
        distance_diffs = np.abs(distances1 - distances2)
        midpoint_diffs /= distances1
        distance_diffs /= distances2

        buffed_d1s = np.repeat(distances1, 3).reshape(vects1.shape)
        buffed_d2s = np.repeat(distances2, 3).reshape(vects2.shape)
        unit_v1s = vects1/buffed_d1s
        unit_v2s = vects2/buffed_d2s
        dots = np.abs(unit_v1s[:,0]*unit_v2s[:,0] + unit_v1s[:,1]*unit_v2s[:,1] + unit_v1s[:,2]*unit_v2s[:,2])

        return midpoint_diffs + distance_diffs + dots


#############################

class Introduction(TeacherStudentsScene):
    def construct(self):
        self.play(self.get_teacher().change_mode, "hooray")
        self.random_blink()
        self.teacher_says("")
        for pi in self.get_students():
            pi.generate_target()
            pi.target.change_mode("happy")            
            pi.target.look_at(self.get_teacher().bubble)
        self.play(*list(map(MoveToTarget, self.get_students())))
        self.random_blink(3)
        self.teacher_says(
            "Here's why \\\\ I'm excited...",
            target_mode = "hooray"
        )
        for pi in self.get_students():
            pi.target.look_at(self.get_teacher().eyes)
        self.play(*list(map(MoveToTarget, self.get_students())))
        self.wait()

class WhenIWasAKid(TeacherStudentsScene):
    def construct(self):
        children = self.get_children()
        speaker = self.get_speaker()

        self.prepare_everyone(children, speaker)
        self.state_excitement(children, speaker)
        self.students = children
        self.teacher = speaker
        self.run_class()
        self.grow_up()

    def state_excitement(self, children, speaker):
        self.teacher_says(
            """
            Here's why 
            I'm excited!
            """,
            target_mode = "hooray"
        )
        self.play_student_changes(*["happy"]*3)
        self.wait()

        speaker.look_at(children)
        me = children[-1]
        self.play(
            FadeOut(self.get_students()),
            FadeOut(self.get_teacher().bubble),
            FadeOut(self.get_teacher().bubble.content),
            Transform(self.get_teacher(), me)
        )
        self.remove(self.get_teacher())
        self.add(me)
        self.play(*list(map(FadeIn, children[:-1] + [speaker])))
        self.random_blink()

    def run_class(self):
        children = self.students
        speaker = self.teacher
        title = OldTexText("Topology")
        title.to_edge(UP)
        pi1, pi2, pi3, me = children

        self.random_blink()
        self.teacher_says(
            """
            Math! Excitement!
            You are the future!
            """,
            target_mode = "hooray"
        )
        self.play(
            pi1.look_at, pi2.eyes,
            pi1.change_mode, "erm",
            pi2.look_at, pi1.eyes,
            pi2.change_mode, "surprised",
        )
        self.play(
            pi3.look_at, me.eyes,
            pi3.change_mode, "sassy",
            me.look_at, pi3.eyes,
        )
        self.random_blink(2)

        self.play(
            self.teacher.change_mode, "speaking",
            FadeOut(self.teacher.bubble),
            FadeOut(self.teacher.bubble.content),
        )
        self.play(Write(title))
        self.random_blink()
        
        self.play(pi1.change_mode, "raise_right_hand")
        self.random_blink()
        self.play(
            pi2.change_mode, "confused",
            pi3.change_mode, "happy",
            pi2.look_at, pi3.eyes,
            pi3.look_at, pi2.eyes,
        )
        self.random_blink()
        self.play(me.change_mode, "pondering")
        self.wait()
        self.random_blink(2)
        self.play(pi1.change_mode, "raise_left_hand")
        self.wait()
        self.play(pi2.change_mode, "erm")
        self.random_blink()
        self.student_says(
            "How is this math?",
            index = -1,
            target_mode = "pleading",
            width = 5, 
            height = 3,
            direction = RIGHT
        )
        self.play(
            pi1.change_mode, "pondering",
            pi2.change_mode, "pondering",
            pi3.change_mode, "pondering",
        )
        self.play(speaker.change_mode, "pondering")
        self.random_blink()

    def grow_up(self):
        me = self.students[-1]
        self.students.remove(me)
        morty = Mortimer(mode = "pondering")
        morty.flip()
        morty.move_to(me, aligned_edge = DOWN)
        morty.to_edge(LEFT)
        morty.look(RIGHT)

        self.play(
            Transform(me, morty),
            *list(map(FadeOut, [
                self.students, self.teacher,
                me.bubble, me.bubble.content
            ]))
        )
        self.remove(me)
        self.add(morty)
        self.play(Blink(morty))
        self.wait()
        self.play(morty.change_mode, "hooray")
        self.wait()


    def prepare_everyone(self, children, speaker):
        self.everyone = list(children) + [speaker]
        for pi in self.everyone:
            pi.bubble = None

    def get_children(self):
        colors = [MAROON_E, YELLOW_D, PINK, GREY_BROWN]
        children = VGroup(*[
            BabyPiCreature(color = color)
            for color in colors
        ])
        children.arrange(RIGHT)
        children.to_edge(DOWN, buff = LARGE_BUFF)
        children.to_edge(LEFT)
        return children

    def get_speaker(self):
        speaker = Mathematician(mode = "happy")
        speaker.flip()
        speaker.to_edge(DOWN, buff = LARGE_BUFF)
        speaker.to_edge(RIGHT)
        return speaker

    def get_pi_creatures(self):
        if hasattr(self, "everyone"):
            return self.everyone
        else:
            return TeacherStudentsScene.get_pi_creatures(self)

class FormingTheMobiusStrip(Scene):
    def construct(self):
        pass

class DrawLineOnMobiusStrip(Scene):
    def construct(self):
        pass

class MugIntoTorus(Scene):
    def construct(self):
        pass

class DefineInscribedSquareProblem(ClosedLoopScene):
    def construct(self):
        self.draw_loop()
        self.cycle_through_shapes()
        self.ask_about_rectangles()

    def draw_loop(self):
        self.title = OldTexText("Inscribed", "square", "problem")
        self.title.to_edge(UP)

        #Draw loop
        self.remove(self.loop)
        self.play(Write(self.title))
        self.wait()
        self.play(ShowCreation(
            self.loop, 
            run_time = 5, 
            rate_func=linear
        ))
        self.wait()
        self.add_rect_dots(square = True)
        self.play(ShowCreation(self.dots, run_time = 2))
        self.wait()
        self.add_connecting_lines(cyclic = True)
        self.play(
            ShowCreation(
                self.connecting_lines,
                lag_ratio = 0,
                run_time = 2
            ),
            Animation(self.dots)
        )
        self.wait(2)

    def cycle_through_shapes(self):
        circle = Circle(radius = 2.5, color = WHITE)
        ellipse = circle.copy()
        ellipse.stretch(1.5, 0)
        ellipse.stretch(0.7, 1)
        ellipse.rotate(-np.pi/2)
        ellipse.set_height(4)
        pi_loop = OldTex("\\pi")[0]
        pi_loop.set_fill(opacity = 0)
        pi_loop.set_stroke(
            color = WHITE,
            width = DEFAULT_STROKE_WIDTH
        )
        pi_loop.set_height(4)
        randy = Randolph()
        randy.look(DOWN)
        randy.set_width(pi_loop.get_width())
        randy.move_to(pi_loop, aligned_edge = DOWN)
        randy.body.set_fill(opacity = 0)
        randy.mouth.set_stroke(width = 0)

        self.transform_loop(circle)
        self.remove(self.loop)
        self.loop = circle
        self.add(self.loop, self.connecting_lines, self.dots)
        self.wait()
        odd_eigths = np.linspace(1./8, 7./8, 4)
        self.move_dots_to_alphas(odd_eigths)
        self.wait()
        for nudge in 0.1, -0.1, 0:
            self.move_dots_to_alphas(odd_eigths+nudge)
        self.wait()
        self.transform_loop(ellipse)
        self.wait()
        nudge = 0.055
        self.move_dots_to_alphas(
            odd_eigths + [nudge, -nudge, nudge, -nudge]
        )
        self.wait(2)
        self.transform_loop(pi_loop)
        self.let_dots_wonder()
        randy_anims = [
            FadeIn(randy),
            Animation(randy),            
            Blink(randy),
            Animation(randy),         
            Blink(randy),
            Animation(randy),
            Blink(randy, rate_func = smooth)
        ]
        for anim in randy_anims:
            self.let_dots_wonder(
                run_time = 1.5,
                random_seed = 0,
                added_anims = [anim]
            )
        self.remove(randy)
        self.transform_loop(self.get_default_loop())

    def ask_about_rectangles(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)
        morty.to_edge(RIGHT)

        new_title = OldTexText("Inscribed", "rectangle", "problem")
        new_title.set_color_by_tex("rectangle", YELLOW)
        new_title.to_edge(UP)
        rect_dots = self.get_rect_vertex_dots()
        rect_alphas = self.get_dot_alphas(rect_dots)

        self.play(FadeIn(morty))
        self.play(morty.change_mode, "speaking")
        self.play(Transform(self.title, new_title))
        self.move_dots_to_alphas(rect_alphas)
        self.wait()
        self.play(morty.change_mode, "hooray")
        self.play(Blink(morty))
        self.wait()
        self.play(FadeOut(self.connecting_lines))
        self.connecting_lines = VGroup()
        self.play(morty.change_mode, "plain")

        dot_pairs = [
            VGroup(self.dots[i], self.dots[j])
            for i, j in [(0, 2), (1, 3)]
        ]
        pair_colors = MAROON_B, PURPLE_B
        diag_lines = [
            Line(d1.get_center(), d2.get_center(), color = c)
            for (d1, d2), c in zip(dot_pairs, pair_colors)
        ]

        for pair, line in zip(dot_pairs, diag_lines):
            self.play(
                FadeIn(line),
                pair.set_color, line.get_color(),
            )

class RectangleProperties(Scene):
    def construct(self):
        rect = Rectangle(color = BLUE)
        vertex_dots = VGroup(*[
            Dot(anchor, color = YELLOW)
            for anchor in rect.get_anchors_and_handles()[0]
        ])
        dot_pairs = [
            VGroup(vertex_dots[i], vertex_dots[j])
            for i, j in [(0, 2), (1, 3)]
        ]
        colors = [MAROON_B, PURPLE_B]
        diag_lines = [
            Line(d1.get_center(), d2.get_center(), color = c)
            for (d1, d2), c in zip(dot_pairs, colors)
        ]
        braces = [Brace(rect).next_to(ORIGIN, DOWN) for x in range(2)]
        for brace, line in zip(braces, diag_lines):
            brace.stretch_to_fit_width(line.get_length())
            brace.rotate(line.get_angle())
        a, b, c, d = labels = VGroup(*[
            OldTex(s).next_to(dot, dot.get_center(), buff = SMALL_BUFF)
            for s, dot in zip("abcd", vertex_dots)
        ])
        midpoint = Dot(ORIGIN, color = RED)


        self.play(ShowCreation(rect))
        self.wait()
        self.play(
            ShowCreation(vertex_dots),
            Write(labels)
        )
        self.wait()
        mob_lists = [
            (a, c, dot_pairs[0]),
            (b, d, dot_pairs[1]),
        ]
        for color, mob_list in zip(colors, mob_lists):
            self.play(*[
                ApplyMethod(mob.set_color, color)
                for mob in mob_list
            ])
            self.wait()
        for line, brace in zip(diag_lines, braces):
            self.play(
                ShowCreation(line),
                GrowFromCenter(brace)
            )
            self.wait()
            self.play(FadeOut(brace))
        self.play(FadeIn(midpoint))
        self.wait()

class PairOfPairBecomeRectangle(Scene):
    def construct(self):
        dots = VGroup(
            Dot(4*RIGHT+0.5*DOWN, color = MAROON_B),
            Dot(5*RIGHT+3*UP, color = MAROON_B),
            Dot(LEFT+0.1*DOWN, color = PURPLE_B),
            Dot(2*LEFT+UP, color = PURPLE_B)
        )
        labels = VGroup()
        for dot, char in zip(dots, "acbd"):
            label = OldTex(char)
            y_coord = dot.get_center()[1]
            label.next_to(dot, np.sign(dot.get_center()[1])*UP)
            label.set_color(dot.get_color())
            labels.add(label)
        lines = [
            Line(
                dots[i].get_center(), 
                dots[j].get_center(), 
                color = dots[i].get_color()
            )
            for i, j in [(0, 1), (2, 3)]
        ]
        groups = [
            VGroup(dots[0], dots[1], labels[0], labels[1], lines[0]),
            VGroup(dots[2], dots[3], labels[2], labels[3], lines[1]),
        ]
        midpoint = Dot(LEFT, color = RED)

        words = VGroup(*list(map(TexText, [
            "Common midpoint",
            "Same distance apart",
            "$\\Downarrow$",
            "Rectangle",
        ])))
        words.arrange(DOWN)
        words.to_edge(RIGHT)
        words[-1].set_color(BLUE)

        self.play(
            ShowCreation(dots),
            Write(labels)
        )
        self.play(*list(map(ShowCreation, lines)))
        self.wait()
        self.play(*[
            ApplyMethod(
                group.shift, 
                -group[-1].get_center()+midpoint.get_center()
            )
            for group in groups
        ])
        self.play(
            ShowCreation(midpoint),
            Write(words[0])
        )
        factor = lines[0].get_length()/lines[1].get_length()        
        grower = groups[1].copy()
        new_line = grower[-1]
        new_line.scale(factor)
        grower[0].move_to(new_line.get_start())
        grower[2].next_to(grower[0], DOWN)
        grower[1].move_to(new_line.get_end())
        grower[3].next_to(grower[1], UP)

        self.play(Transform(groups[1], grower))
        self.play(Write(words[1]))
        self.wait()

        rectangle = Polygon(*[
            dots[i].get_center()
            for i in (0, 2, 1, 3)
        ])
        rectangle.set_color(BLUE)
        self.play(
            ShowCreation(rectangle),
            Animation(dots)
        )
        self.play(*list(map(Write, words[2:])))
        self.wait()

class SearchForRectangleOnLoop(ClosedLoopScene):
    def construct(self):
        self.add_dots_at_alphas(*np.linspace(0.2, 0.8, 4))
        self.set_color_dots_by_pair()
        rect_alphas = self.get_rect_alphas()

        self.play(ShowCreation(self.dots))
        self.add_connecting_lines()
        self.play(ShowCreation(self.connecting_lines))
        self.let_dots_wonder(2)
        self.move_dots_to_alphas(rect_alphas)

        midpoint = Dot(
            center_of_mass([d.get_center() for d in self.dots]),
            color = RED
        )
        self.play(ShowCreation(midpoint))
        self.wait()
        angles = [line.get_angle() for line in self.connecting_lines]
        angle_mean = np.mean(angles)
        self.play(
            *[
                ApplyMethod(line.rotate, angle_mean-angle)
                for line, angle in zip(self.connecting_lines, angles)
            ] + [Animation(midpoint)],
            rate_func = there_and_back
        )
        self.add(self.connecting_lines.copy(), midpoint)
        self.connecting_lines = VGroup()
        self.wait()
        self.add_connecting_lines(cyclic = True)
        self.play(
            ShowCreation(self.connecting_lines), 
            Animation(self.dots)
        )
        self.wait()

class DeclareFunction(ClosedLoopScene):
    def construct(self):
        self.add_dots_at_alphas(0.2, 0.8)
        self.set_color_dots_by_pair()        
        self.add_connecting_lines()
        VGroup(
            self.loop, self.dots, self.connecting_lines
        ).scale(0.7).to_edge(LEFT).shift(DOWN)
        arrow = Arrow(LEFT, RIGHT).next_to(self.loop)
        self.add(arrow)

        self.add_tex()
        self.let_dots_wonder(10)

    def add_tex(self):
        tex = OldTex("f", "(A, B)", "=", "(x, y, z)")
        tex.to_edge(UP)
        tex.shift(LEFT)

        ab_brace = Brace(tex[1])
        xyz_brace = Brace(tex[-1], RIGHT)
        ab_brace.add(ab_brace.get_text("Pair of points on the loop"))
        xyz_brace.add(xyz_brace.get_text("Point in 3d space"))
        ab_brace.set_color_by_gradient(MAROON_B, PURPLE_B)
        xyz_brace.set_color(BLUE)

        self.add(tex)
        self.play(Write(ab_brace))
        self.wait()
        self.play(Write(xyz_brace))
        self.wait()

class DefinePairTo3dFunction(Scene):
    def construct(self):
        pass

class LabelMidpoint(Scene):
    def construct(self):
        words = OldTexText("Midpoint $M$")
        words.set_color(RED)
        words.scale(2)
        self.play(Write(words, run_time = 1))
        self.wait()

class LabelDistance(Scene):
    def construct(self):
        words = OldTexText("Distance $d$")
        words.set_color(MAROON_B)
        words.scale(2)
        self.play(Write(words, run_time = 1))
        self.wait()

class DrawingOneLineOfTheSurface(Scene):
    def construct(self):
        pass

class FunctionSurface(Scene):
    def construct(self):
        pass

class PointPairApprocahingEachother3D(Scene):
    def construct(self):
        pass

class InputPairToFunction(Scene):
    def construct(self):
        tex = OldTex("f(X, X)", "=X")
        tex.set_color_by_tex("=X", BLUE)
        tex.scale(2)
        self.play(Write(tex[0]))
        self.wait(2)
        self.play(Write(tex[1]))
        self.wait(2)

class WigglePairUnderSurface(Scene):
    def construct(self):
        pass        

class WriteContinuous(Scene):
    def construct(self):
        self.play(Write(OldTexText("Continuous").scale(2)))
        self.wait(2)

class DistinctPairCollisionOnSurface(Scene):
    def construct(self):
        pass

class PairsOfPointsOnLoop(ClosedLoopScene):
    def construct(self):
        self.add_dots_at_alphas(0.2, 0.5)
        self.dots.set_color(MAROON_B)
        self.add_connecting_lines()
        self.let_dots_wonder(run_time = 10)

class PairOfRealsToPlane(Scene):
    def construct(self):
        r1, r2 = numbers = -3, 2
        colors = GREEN, RED
        dot1, dot2 = dots = VGroup(*[Dot(color = c) for c in colors])
        for dot, number in zip(dots, numbers):
            dot.move_to(number*RIGHT)
        pair_label = OldTex("(", str(r1), ",", str(r2), ")")
        for number, color in zip(numbers, colors):
            pair_label.set_color_by_tex(str(number), color)
        pair_label.next_to(dots, UP, buff = 2)
        arrows = VGroup(*[
            Arrow(pair_label[i], dot, color = dot.get_color())
            for i, dot in zip([1, 3], dots)
        ])
        two_d_point = Dot(r1*RIGHT + r2*UP, color = YELLOW)
        pair_label.add_background_rectangle()

        x_axis = NumberLine(color = BLUE)
        y_axis = NumberLine(color = BLUE)
        plane = NumberPlane().fade()

        self.add(x_axis, y_axis, dots, pair_label)
        self.play(ShowCreation(arrows, run_time = 2))
        self.wait()
        self.play(
            pair_label.next_to, two_d_point, UP+LEFT, SMALL_BUFF,
            Rotate(y_axis, np.pi/2),
            Rotate(dot2, np.pi/2),
            FadeOut(arrows)
        )
        lines = VGroup(*[
            DashedLine(dot, two_d_point, color = dot.get_color())
            for dot in dots
        ])
        self.play(*list(map(ShowCreation, lines)))
        self.play(ShowCreation(two_d_point))
        everything = VGroup(*self.get_mobjects())
        self.play(
            FadeIn(plane), 
            Animation(everything),
            Animation(dot2)
        )
        self.wait()

class SeekSurfaceForPairs(ClosedLoopScene):
    def construct(self):
        self.loop.to_edge(LEFT)
        self.add_dots_at_alphas(0.2, 0.3)
        self.set_color_dots_by_pair()        
        self.add_connecting_lines()

        arrow = Arrow(LEFT, RIGHT).next_to(self.loop)
        words = OldTexText("Some 2d surface")
        words.next_to(arrow, RIGHT)

        anims = [
            ShowCreation(arrow),
            Write(words)
        ]
        for anim in anims:
            self.let_dots_wonder(
                random_seed = 1,
                added_anims = [anim],
                run_time = anim.run_time
            )
        self.let_dots_wonder(random_seed = 1, run_time = 10)

class AskAbouPairType(TeacherStudentsScene):
    def construct(self):
        self.student_says("""
            Do you mean ordered
            or unordered pairs?
        """)
        self.play(*[
            ApplyMethod(self.get_students()[i].change_mode, "confused")
            for i in (0, 2)
        ])
        self.random_blink(3)

class DefineOrderedPair(ClosedLoopScene):
    def construct(self):
        title = OldTexText("Ordered pairs")
        title.to_edge(UP)
        subtitle = OldTex(
            "(", "a", ",", "b", ")", 
            "\\ne", 
            "(", "b", ",", "a", ")"
        )
        labels_start = VGroup(subtitle[1], subtitle[3])
        labels_end = VGroup(subtitle[9], subtitle[7])
        subtitle.next_to(title, DOWN)
        colors = GREEN, RED
        for char, color in zip("ab", colors):
            subtitle.set_color_by_tex(char, color)
        self.loop.next_to(subtitle, DOWN)
        self.add(title, subtitle)

        self.add_dots_at_alphas(0.5, 0.6)
        dots = self.dots
        for dot, color, char in zip(dots, colors, "ab"):
            dot.set_color(color)
            label = OldTex(char)
            label.set_color(color)
            label.next_to(dot, RIGHT, buff = SMALL_BUFF)
            dot.label = label
        self.dots[1].label.shift(0.3*UP)
        first = OldTexText("First")
        first.next_to(self.dots[0], UP+2*LEFT, LARGE_BUFF)
        arrow = Arrow(first.get_bottom(), self.dots[0], color = GREEN)

        self.wait()
        self.play(*[
            Transform(label.copy(), dot.label)
            for label, dot in zip(labels_start, dots)
        ])
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(*[d.label for d in dots])
        self.wait()
        self.play(
            Write(first),
            ShowCreation(arrow)
        )
        self.wait()

class DefineUnorderedPair(ClosedLoopScene):
    def construct(self):
        title = OldTexText("Unordered pairs")
        title.to_edge(UP)
        subtitle = OldTex(
            "\\{a,b\\}",
            "=",
            "\\{b,a\\}",
        )
        subtitle.next_to(title, DOWN)
        for char in "ab":
            subtitle.set_color_by_tex(char, PURPLE_B)
        self.loop.next_to(subtitle, DOWN)
        self.add(title, subtitle)

        self.add_dots_at_alphas(0.5, 0.6)
        dots = self.dots
        dots.set_color(PURPLE_B)

        labels = VGroup(*[subtitle[i].copy() for i in (0, 2)])
        for label, vect in zip(labels, [LEFT, RIGHT]):
            label.next_to(dots, vect, LARGE_BUFF)
        arrows = [
            Arrow(*pair, color = PURPLE_B)
            for pair in it.product(labels, dots)
        ]
        arrow_pairs = [VGroup(*arrows[:2]), VGroup(*arrows[2:])]

        for label, arrow_pair in zip(labels, arrow_pairs):
            self.play(*list(map(FadeIn, [label, arrow_pair])))
            self.wait()
        for x in range(2):
            self.play(
                dots[0].move_to, dots[1],
                dots[1].move_to, dots[0],
                path_arc = np.pi/2
            )
            self.wait()

class BeginWithOrdered(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            One must know order
            before he can ignore it.
        """)
        self.random_blink(3)

class DeformToInterval(ClosedLoopScene):
    def construct(self):
        interval = UnitInterval(color = WHITE)
        interval.shift(2*DOWN)
        numbers = interval.get_number_mobjects(0, 1)
        line = Line(interval.get_left(), interval.get_right())
        line.insert_n_curves(self.loop.get_num_curves())
        line.make_smooth()

        self.loop.scale(0.7)
        self.loop.to_edge(UP)
        original_loop = self.loop.copy()
        cut_loop = self.loop.copy()
        cut_loop.get_points()[0] += 0.3*(UP+RIGHT)
        cut_loop.get_points()[-1] += 0.3*(DOWN+RIGHT)

        #Unwrap loop
        self.transform_loop(cut_loop, path_arc = np.pi)
        self.wait()
        self.transform_loop(
            line,
            run_time = 3,
            path_arc = np.pi/2
        )
        self.wait()
        self.play(ShowCreation(interval))
        self.play(Write(numbers))
        self.wait()

        #Follow points
        self.loop = original_loop.copy()
        self.play(FadeIn(self.loop))
        self.add(original_loop)
        self.add_dots_at_alphas(*np.linspace(0, 1, 20))
        self.dots.set_color_by_gradient(BLUE, MAROON_C, BLUE)
        dot_at_1 = self.dots[-1]
        dot_at_1.generate_target()
        dot_at_1.target.move_to(interval.get_right())
        dots_copy = self.dots.copy()
        fading_dots = VGroup(*list(self.dots)+list(dots_copy))
        end_dots = VGroup(
            self.dots[0], self.dots[-1],
            dots_copy[0], dots_copy[-1]
        )
        fading_dots.remove(*end_dots)

        self.play(Write(self.dots))
        self.add(dots_copy)
        self.wait()
        self.transform_loop(
            line, 
            added_anims = [MoveToTarget(dot_at_1)],
            run_time = 3
        )
        self.wait()
        self.loop = original_loop
        self.dots = dots_copy
        dot_at_1 = self.dots[-1]
        dot_at_1.target.move_to(cut_loop.get_points()[-1])
        self.transform_loop(
            cut_loop,
            added_anims = [MoveToTarget(dot_at_1)]
        )
        self.wait()
        fading_dots.generate_target()
        fading_dots.target.set_fill(opacity = 0.3)
        self.play(MoveToTarget(fading_dots))
        self.play(
            end_dots.shift, 0.2*UP, 
            rate_func = wiggle
        )
        self.wait()

class RepresentPairInUnitSquare(ClosedLoopScene):
    def construct(self):
        interval = UnitInterval(color = WHITE)
        interval.shift(2.5*DOWN)
        interval.shift(LEFT)
        numbers = interval.get_number_mobjects(0, 1)
        line = Line(interval.get_left(), interval.get_right())
        line.insert_n_curves(self.loop.get_num_curves())
        line.make_smooth()
        vert_interval = interval.copy()
        square = Square()
        square.set_width(interval.get_width())
        square.set_stroke(width = 0)
        square.set_fill(color = BLUE, opacity = 0.3)
        square.move_to(
            interval.get_left(),
            aligned_edge = DOWN+LEFT
        )

        right_words = VGroup(*[
            OldTexText("Pair of\\\\ loop points"),
            OldTex("\\Downarrow"),
            OldTexText("Point in \\\\ unit square")
        ])
        right_words.arrange(DOWN)
        right_words.to_edge(RIGHT)

        dot_coords = (0.3, 0.7)
        self.loop.scale(0.7)
        self.loop.to_edge(UP)
        self.add_dots_at_alphas(*dot_coords)
        self.dots.set_color_by_gradient(GREEN, RED)

        self.play(
            Write(self.dots),
            Write(right_words[0])
        )
        self.wait()
        self.transform_loop(line)
        self.play(
            ShowCreation(interval),
            Write(numbers),
            Animation(self.dots)
        )
        self.wait()
        self.play(*[
            Rotate(mob, np.pi/2, about_point = interval.get_left())
            for mob in (vert_interval, self.dots[1])
        ])

        #Find interior point
        point = self.dots[0].get_center()[0]*RIGHT
        point += self.dots[1].get_center()[1]*UP
        inner_dot = Dot(point, color = YELLOW)
        dashed_lines = VGroup(*[
            DashedLine(dot, inner_dot, color = dot.get_color())
            for dot in self.dots
        ])
        self.play(ShowCreation(dashed_lines))
        self.play(ShowCreation(inner_dot))
        self.play(
            FadeIn(square),
            Animation(self.dots),
            *list(map(Write, right_words[1:]))
        )
        self.wait()

        #Shift point in square

        movers = list(dashed_lines)+list(self.dots)+[inner_dot]
        for mob in movers:
            mob.generate_target()
        shift_vals = [
            RIGHT+DOWN, 
            LEFT+DOWN, 
            LEFT+2*UP,
            3*DOWN,
            2*RIGHT+UP,
            RIGHT+UP,
            3*LEFT+3*DOWN
        ]
        for shift_val in shift_vals:
            inner_dot.target.shift(shift_val)
            self.dots[0].target.shift(shift_val[0]*RIGHT)
            self.dots[1].target.shift(shift_val[1]*UP)
            for line, dot in zip(dashed_lines, self.dots):
                line.target.put_start_and_end_on(
                    dot.target.get_center(), 
                    inner_dot.target.get_center()
                )
            self.play(*list(map(MoveToTarget, movers)))
        self.wait()
        self.play(*list(map(FadeOut, [dashed_lines, self.dots])))

class EdgesOfSquare(Scene):
    def construct(self):
        square = self.add_square()
        x_edges, y_edges = self.get_edges(square)
        label_groups = self.get_coordinate_labels(square)
        arrow_groups = self.get_arrows(x_edges, y_edges)

        for edge in list(x_edges) + list(y_edges):
            self.play(ShowCreation(edge))
        self.wait()
        for label_group in label_groups:
            for label in label_group[:3]:
                self.play(FadeIn(label))
            self.wait()
            self.play(Write(VGroup(*label_group[3:])))
            self.wait()
        self.play(FadeOut(VGroup(*label_groups)))
        for arrows in arrow_groups:
            self.play(ShowCreation(arrows, run_time = 2))
            self.wait()
        self.play(*[
            ApplyMethod(
                n.next_to,
                square.get_corner(vect+LEFT),
                LEFT,
                MED_SMALL_BUFF,
                path_arc = np.pi/2
            )
            for n, vect in zip(self.numbers, [DOWN, UP])
        ])
        self.wait()

    def add_square(self):
        interval = UnitInterval(color = WHITE)
        interval.shift(2.5*DOWN)
        bottom_left = interval.get_left()
        for tick in interval.tick_marks:
            height = tick.get_height()
            tick.scale(0.5)
            tick.shift(height*DOWN/4.)
        self.numbers = interval.get_number_mobjects(0, 1)
        vert_interval = interval.copy()
        vert_interval.rotate(np.pi, axis = UP+RIGHT, about_point = bottom_left)
        square = Square()
        square.set_width(interval.get_width())
        square.set_stroke(width = 0)
        square.set_fill(color = BLUE, opacity = 0.3)
        square.move_to(
            bottom_left,
            aligned_edge = DOWN+LEFT
        )
        self.add(interval, self.numbers, vert_interval, square)
        return square

    def get_edges(self, square):
        y_edges = VGroup(*[
            Line(
                square.get_corner(vect+LEFT),
                square.get_corner(vect+RIGHT),
            )
            for vect in (DOWN, UP)
        ])
        y_edges.set_color(BLUE)
        x_edges = VGroup(*[
            Line(
                square.get_corner(vect+DOWN),
                square.get_corner(vect+UP),
            )
            for vect in (LEFT, RIGHT)
        ])
        x_edges.set_color(MAROON_B)
        return x_edges, y_edges

    def get_coordinate_labels(self, square):
        alpha_range = np.arange(0, 1.1, 0.1)
        dot_groups = [
            VGroup(*[
                Dot(interpolate(
                    square.get_corner(DOWN+vect),
                    square.get_corner(UP+vect),
                    alpha
                ))
                for alpha in alpha_range
            ])
            for vect in (LEFT, RIGHT)            
        ]
        for group in dot_groups:
            group.set_color_by_gradient(YELLOW, PURPLE_B)
        label_groups = [
            VGroup(*[
                OldTex("(%s, %s)"%(a, b)).scale(0.7)
                for b in alpha_range
            ])
            for a in (0, 1)
        ]
        for dot_group, label_group in zip(dot_groups, label_groups):
            for dot, label in zip(dot_group, label_group):
                label[1].set_color(MAROON_B)
                label.next_to(dot, RIGHT*np.sign(dot.get_center()[0]))
                label.add(dot)
        return label_groups

    def get_arrows(self, x_edges, y_edges):
        alpha_range = np.linspace(0, 1, 4)
        return [
            VGroup(*[
                VGroup(*[
                    Arrow(
                        edge.point_from_proportion(a1),
                        edge.point_from_proportion(a2),
                        buff = 0
                    )
                    for a1, a2 in zip(alpha_range, alpha_range[1:])
                ])
                for edge in edges
            ]).set_color(edges.get_color())
            for edges in (x_edges, y_edges)
        ]

class EndpointsGluedTogether(ClosedLoopScene):
    def construct(self):
        interval = UnitInterval(color = WHITE)
        interval.shift(2*DOWN)
        numbers = interval.get_number_mobjects(0, 1)
        line = Line(interval.get_left(), interval.get_right())
        line.insert_n_curves(self.loop.get_num_curves())
        line.make_smooth()

        self.loop.scale(0.7)
        self.loop.to_edge(UP)
        original_loop = self.loop
        self.remove(original_loop)

        self.loop = line
        dots = VGroup(*[
            Dot(line.get_bounding_box_point(vect))
            for vect in (LEFT, RIGHT)
        ])
        dots.set_color(BLUE)

        self.add(interval, dots)
        self.play(dots.rotate, np.pi/20, rate_func = wiggle)
        self.wait()
        self.transform_loop(
            original_loop,
            added_anims = [
                ApplyMethod(dot.move_to, original_loop.get_points()[0])
                for dot in dots
            ],
            run_time = 3
        )
        self.wait()

class WrapUpToTorus(Scene):
    def construct(self):
        pass

class TorusPlaneAnalogy(ClosedLoopScene):
    def construct(self):
        top_arrow = DoubleArrow(LEFT, RIGHT)
        top_arrow.to_edge(UP, buff = 2*LARGE_BUFF)
        single_pointed_top_arrow = Arrow(LEFT, RIGHT)
        single_pointed_top_arrow.to_edge(UP, buff = 2*LARGE_BUFF)        
        low_arrow = DoubleArrow(LEFT, RIGHT).shift(2*DOWN)
        self.loop.scale(0.5)
        self.loop.next_to(top_arrow, RIGHT)
        self.loop.shift_onto_screen()
        self.add_dots_at_alphas(0.3, 0.5)
        self.dots.set_color_by_gradient(GREEN, RED)

        plane = NumberPlane()
        plane.scale(0.3).next_to(low_arrow, LEFT)
        number_line = NumberLine()
        number_line.scale(0.3)
        number_line.next_to(low_arrow, RIGHT)
        number_line.add(
            Dot(number_line.number_to_point(3), color = GREEN),
            Dot(number_line.number_to_point(-2), color = RED),
        )

        self.wait()
        self.play(ShowCreation(single_pointed_top_arrow))
        self.wait()
        self.play(ShowCreation(top_arrow))
        self.wait()
        self.play(ShowCreation(plane))
        self.play(ShowCreation(low_arrow))
        self.play(ShowCreation(number_line))
        self.wait()

class WigglingPairOfPoints(ClosedLoopScene):
    def construct(self):
        alpha_pairs = [
            (0.4, 0.6),
            (0.42, 0.62),
        ]
        self.add_dots_at_alphas(*alpha_pairs[-1])
        self.add_connecting_lines()
        self.dots.set_color_by_gradient(GREEN, RED)
        self.connecting_lines.set_color(YELLOW)
        for x, pair in zip(list(range(20)), it.cycle(alpha_pairs)):
            self.move_dots_to_alphas(pair, run_time = 0.3)


class WigglingTorusPoint(Scene):
        def construct(self):
            pass    

class WhatAboutUnordered(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What about \\\\ unordered pairs?"
        )
        self.play(self.get_teacher().change_mode, "pondering")
        self.random_blink(2)

class TrivialPairCollision(ClosedLoopScene):
    def construct(self):
        self.loop.to_edge(RIGHT)
        self.add_dots_at_alphas(0.35, 0.55)
        self.dots.set_color_by_gradient(BLUE, YELLOW)
        a, b = self.dots
        a_label = OldTex("a").next_to(a, RIGHT)
        a_label.set_color(a.get_color())
        b_label = OldTex("b").next_to(b, LEFT)
        b_label.set_color(b.get_color())
        line = Line(
            a.get_corner(DOWN+LEFT),
            b.get_corner(UP+RIGHT),
            color = MAROON_B
        )
        midpoint = Dot(self.dots.get_center(), color = RED)
        randy = Randolph(mode = "pondering")
        randy.next_to(self.loop, LEFT, aligned_edge = DOWN)
        randy.look_at(b)
        self.add(randy)

        for label in a_label, b_label:
            self.play(
                Write(label, run_time = 1),
                randy.look_at, label
            )
        self.play(Blink(randy))
        self.wait()
        swappers = [a, b, a_label, b_label]
        for mob in swappers:
            mob.save_state()
        self.play(
            a.move_to, b,
            b.move_to, a,
            a_label.next_to, b, LEFT,
            b_label.next_to, a, RIGHT,
            randy.look_at, a,
            path_arc = np.pi
        )
        self.play(ShowCreation(midpoint))
        self.play(ShowCreation(line), Animation(midpoint))
        self.play(randy.change_mode, "erm", randy.look_at, b)
        self.play(
            randy.look_at, a,
            *[m.restore for m in swappers],
            path_arc = -np.pi
        )
        self.play(Blink(randy))
        self.wait()

class NotHelpful(Scene):
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)
        bubble = morty.get_bubble(SpeechBubble, width = 4, height = 3)
        bubble.write("Not helpful!")

        self.add(morty)
        self.play(
            FadeIn(bubble),
            FadeIn(bubble.content),
            morty.change_mode, "angry",
            morty.look, OUT
        )
        self.play(Blink(morty))
        self.wait()

class FoldUnitSquare(EdgesOfSquare):
    def construct(self):    
        self.add_triangles()
        self.add_arrows()
        self.show_points_to_glue()
        self.perform_fold()
        self.show_singleton_pairs()
        self.ask_about_gluing()
        self.clarify_edge_gluing()

    def add_triangles(self):
        square = self.add_square()
        triangles = VGroup(*[
            Polygon(*[square.get_corner(vect) for vect in vects])
            for vects in [
                (DOWN+LEFT, UP+RIGHT, UP+LEFT),            
                (DOWN+LEFT, UP+RIGHT, DOWN+RIGHT),
            ]
        ])
        triangles.set_stroke(width = 0)
        triangles.set_fill(
            color = square.get_color(), 
            opacity = square.get_fill_opacity()
        )
        self.remove(square)
        self.square = square
        self.add(triangles)
        self.triangles = triangles

    def add_arrows(self):
        start_arrows = VGroup()
        end_arrows = VGroup()
        colors = MAROON_B, BLUE
        for a in 0, 1:        
            for color in colors:
                b_range = np.linspace(0, 1, 4)
                for b1, b2 in zip(b_range, b_range[1:]):
                    arrow = Arrow(
                        self.get_point_from_coords(a, b1),
                        self.get_point_from_coords(a, b2),
                        buff = 0,
                        color = color
                    )
                    if color is BLUE:
                        arrow.rotate(
                            -np.pi/2, 
                            about_point = self.square.get_center()
                        )
                    if (a is 0):
                        start_arrows.add(arrow)
                    else:
                        end_arrows.add(arrow)
        self.add(start_arrows, end_arrows)
        self.start_arrows = start_arrows
        self.end_arrows = VGroup(*list(end_arrows[3:])+list(end_arrows[:3])).copy()
        self.end_arrows.set_color(
            color_gradient([MAROON_B, BLUE], 3)[1]
        )

    def show_points_to_glue(self):
        colors = YELLOW, MAROON_B, PINK
        pairs = [(0.2, 0.3), (0.5, 0.7), (0.25, 0.6)]
        unit = self.square.get_width()

        start_dots = VGroup()
        end_dots = VGroup()
        for (x, y), color in zip(pairs, colors):
            old_x_line, old_y_line = None, None
            for (a, b) in (x, y), (y, x):
                point = self.get_point_from_coords(a, b)
                dot = Dot(point)
                dot.set_color(color)
                if color == colors[-1]:
                    s = "(x, y)" if a < b else "(y, x)"
                    label = OldTex(s)
                else:
                    label = OldTex("(%.01f, %.01f)"%(a, b))
                vect = UP+RIGHT if a < b else DOWN+RIGHT
                label.next_to(dot, vect, buff = SMALL_BUFF)

                self.play(*list(map(FadeIn, [dot, label])))
                x_line = Line(point+a*unit*LEFT, point)
                y_line = Line(point+b*unit*DOWN, point)
                x_line.set_color(GREEN)
                y_line.set_color(RED)
                if old_x_line is None:
                    self.play(ShowCreation(x_line), Animation(dot))
                    self.play(ShowCreation(y_line), Animation(dot))
                    old_x_line, old_y_line = y_line, x_line
                else:
                    self.play(Transform(old_x_line, x_line), Animation(dot))
                    self.play(Transform(old_y_line, y_line), Animation(dot))
                    self.remove(old_x_line, old_y_line)
                    self.add(x_line, y_line, dot)
                self.wait(2)
                self.play(FadeOut(label))
                if a < b:
                    start_dots.add(dot)
                else:
                    end_dots.add(dot)
            self.play(*list(map(FadeOut, [x_line, y_line])))
        self.start_dots, self.end_dots = start_dots, end_dots

    def perform_fold(self):
        diag_line = DashedLine(
            self.square.get_corner(DOWN+LEFT),
            self.square.get_corner(UP+RIGHT),
            color = RED
        )

        self.play(ShowCreation(diag_line))
        self.wait()
        self.play(
            Transform(*self.triangles),
            Transform(self.start_dots, self.end_dots),
            Transform(self.start_arrows, self.end_arrows),
        )
        self.wait()
        self.diag_line = diag_line

    def show_singleton_pairs(self):
        xs = [0.7, 0.4, 0.5]
        old_label = None
        old_dot = None
        for x in xs:
            point = self.get_point_from_coords(x, x)
            dot = Dot(point)
            if x is xs[-1]:
                label = OldTex("(x, x)")
            else:
                label = OldTex("(%.1f, %.1f)"%(x, x))
            label.next_to(dot, UP+LEFT, buff = SMALL_BUFF)
            VGroup(dot, label).set_color(RED)
            if old_label is None:
                self.play(
                    ShowCreation(dot),
                    Write(label)
                )
                old_label = label
                old_dot = dot
            else:
                self.play(
                    Transform(old_dot, dot),
                    Transform(old_label, label),
                )
            self.wait()
        #Some strange bug necesitating this
        self.remove(old_label)
        self.add(label)

    def ask_about_gluing(self):
        keepers = VGroup(
            self.triangles[0],
            self.start_arrows,
            self.diag_line
        ).copy()
        faders = VGroup(*self.get_mobjects())
        randy = Randolph()
        randy.next_to(ORIGIN, DOWN)
        bubble = randy.get_bubble(height = 4, width = 6)
        bubble.write("How do you \\\\ glue those arrows?")

        self.play(
            FadeOut(faders),
            Animation(keepers)
        )
        self.play(
            keepers.scale, 0.6,
            keepers.shift, 4*RIGHT + UP,
            FadeIn(randy)
        )
        self.play(
            randy.change_mode, "pondering",
            randy.look_at, keepers,
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(randy))
        self.wait()
        self.randy = randy

    def clarify_edge_gluing(self):
        dots = VGroup(*[
            Dot(self.get_point_from_coords(*coords), radius = 0.1)
            for coords in [
                (0.1, 0),
                (1, 0.1),
                (0.9, 0),
                (1, 0.9),
            ]
        ])
        dots.scale(0.6)
        dots.shift(4*RIGHT + UP)
        for dot in dots[:2]:
            dot.set_color(YELLOW)
            self.play(
                ShowCreation(dot),
                self.randy.look_at, dot
            )
        self.wait()
        for dot in dots[2:]:
            dot.set_color(MAROON_B)
            self.play(
                ShowCreation(dot),
                self.randy.look_at, dot
            )
        self.play(Blink(self.randy))
        self.wait()

    def get_point_from_coords(self, x, y):
        left, right, bottom, top = [
            self.triangles.get_edge_center(vect)
            for vect in (LEFT, RIGHT, DOWN, UP)
        ]
        x_point = interpolate(left, right, x)
        y_point = interpolate(bottom, top, y)
        return x_point[0]*RIGHT + y_point[1]*UP

class PrepareForMobiusStrip(Scene):
    def construct(self):
        self.add_triangles()
        self.perform_cut()
        self.rearrange_pieces()

    def add_triangles(self):
        triangles = VGroup(
            Polygon(
                DOWN+LEFT,
                DOWN+RIGHT,
                ORIGIN,
            ),
            Polygon(
                DOWN+RIGHT,
                UP+RIGHT,          
                ORIGIN,
            ),
        )
        triangles.set_fill(color = BLUE, opacity = 0.6)
        triangles.set_stroke(width = 0)
        triangles.center()
        triangles.scale(2)
        arrows_color = color_gradient([PINK, BLUE], 3)[1]
        for tri in triangles:
            anchors = tri.get_anchors_and_handles()[0]
            alpha_range = np.linspace(0, 1, 4)
            arrows = VGroup(*[
                Arrow(
                    interpolate(anchors[0], anchors[1], a),
                    interpolate(anchors[0], anchors[1], b),
                    buff = 0,
                    color = arrows_color
                )
                for a, b in zip(alpha_range, alpha_range[1:])
            ])
            tri.original_arrows = arrows
            tri.add(arrows)
            i, j, k = (0, 2, 1) if tri is triangles[0] else (1, 2, 0)
            dashed_line = DashedLine(
                anchors[i], anchors[j], 
                color = RED
            )
            tri.add(dashed_line)

            #Add but don't draw cut_arrows
            start, end = anchors[j], anchors[k]
            cut_arrows = VGroup(*[
                Arrow(
                    interpolate(start, end, a),
                    interpolate(start, end, b),
                    buff = 0,
                    color = YELLOW
                )
                for a, b in zip(alpha_range, alpha_range[1:])
            ])
            tri.cut_arrows = cut_arrows
        self.add(triangles)
        self.triangles = triangles

    def perform_cut(self):
        tri1, tri2 = self.triangles


        self.play(ShowCreation(tri1.cut_arrows))
        for tri in self.triangles:
            tri.add(tri.cut_arrows)
        self.wait()
        self.play(
            tri1.shift, (DOWN+LEFT)/2.,
            tri2.shift, (UP+RIGHT)/2.,
        )
        self.wait()

    def rearrange_pieces(self):
        tri1, tri2 = self.triangles
        self.play(
            tri1.rotate, np.pi, UP+RIGHT,
            tri1.next_to, ORIGIN, RIGHT,
            tri2.next_to, ORIGIN, LEFT,
        )
        self.wait()
        self.play(*[
            ApplyMethod(tri.shift, tri.get_points()[0][0]*LEFT)
            for tri in self.triangles
        ])
        self.play(*[
            FadeOut(tri.original_arrows)
            for tri in self.triangles
        ])
        for tri in self.triangles:
            tri.remove(tri.original_arrows)
        self.wait()
        # self.play(*[
        #     ApplyMethod(tri.rotate, -np.pi/4)
        #     for tri in self.triangles
        # ])
        # self.wait()

class FoldToMobius(Scene):
    def construct(self):
        pass

class MobiusPlaneAnalogy(ClosedLoopScene):
    def construct(self):
        top_arrow = Arrow(LEFT, RIGHT)
        top_arrow.to_edge(UP, buff = 2*LARGE_BUFF)
        low_arrow = Arrow(LEFT, RIGHT).shift(2*DOWN)
        self.loop.scale(0.5)
        self.loop.next_to(top_arrow, RIGHT)
        self.loop.shift_onto_screen()
        self.add_dots_at_alphas(0.3, 0.5)
        self.dots.set_color(PURPLE_B)

        plane = NumberPlane()
        plane.scale(0.3).next_to(low_arrow, LEFT)
        number_line = NumberLine()
        number_line.scale(0.3)
        number_line.next_to(low_arrow, RIGHT)
        number_line.add(
            Dot(number_line.number_to_point(3), color = GREEN),
            Dot(number_line.number_to_point(-2), color = RED),
        )

        self.wait()
        self.play(ShowCreation(top_arrow))
        self.wait()
        self.play(ShowCreation(plane))
        self.play(ShowCreation(low_arrow))
        self.play(ShowCreation(number_line))
        self.wait()

class DrawRightArrow(Scene):
    CONFIG = {
        "tex" : "\\Rightarrow"
    }
    def construct(self):
        arrow = OldTex(self.tex)
        arrow.scale(4)
        self.play(Write(arrow))
        self.wait()

class DrawLeftrightArrow(DrawRightArrow):
    CONFIG = {
        "tex" : "\\Leftrightarrow"
    }

class MobiusToPairToSurface(ClosedLoopScene):
    def construct(self):
        self.loop.scale(0.5)
        self.loop.next_to(ORIGIN, RIGHT)
        self.loop.to_edge(UP)
        self.add_dots_at_alphas(0.4, 0.6)
        self.dots.set_color(MAROON_B)
        self.add_connecting_lines()
        strip_dot = Dot().next_to(self.loop, LEFT, buff = 2*LARGE_BUFF)
        surface_dot = Dot().next_to(self.loop, DOWN, buff = 2*LARGE_BUFF)

        top_arrow = Arrow(strip_dot, self.loop)
        right_arrow = Arrow(self.loop, surface_dot)
        diag_arrow = Arrow(strip_dot, surface_dot)

        randy = self.randy = Randolph(mode = "pondering")
        randy.next_to(ORIGIN, DOWN+LEFT)

        self.look_at(strip_dot)
        self.play(
            ShowCreation(top_arrow),
            randy.look_at, self.loop
        )
        self.wait()
        self.look_at(strip_dot, surface_dot)
        self.play(ShowCreation(diag_arrow))
        self.play(Blink(randy))
        self.look_at(strip_dot, self.loop)
        self.wait()
        self.play(
            ShowCreation(right_arrow),
            randy.look_at, surface_dot
        )
        self.play(Blink(randy))
        self.play(randy.change_mode, "happy")
        self.play(Blink(randy))
        self.wait()


    def look_at(self, *things):
        for thing in things:
            self.play(self.randy.look_at, thing)

class MapMobiusStripOntoSurface(Scene):
    def construct(self):
        pass

class StripMustIntersectItself(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            """
            The strip must 
            intersect itself
            during this process
            """,
            width = 4
        )
        dot = Dot(2*UP + 4*LEFT)
        for student in self.get_students():
            student.generate_target()
            student.target.change_mode("pondering")
            student.target.look_at(dot)
        self.play(*list(map(MoveToTarget, self.get_students())))
        self.random_blink(4)

class PairOfMobiusPointsLandOnEachother(Scene):
    def construct(self):
        pass

class ThatsTheProof(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            """
            Bada boom
            bada bang!
            """,
            target_mode = "hooray",
            width = 4
        )
        self.play_student_changes(*["hooray"]*3)
        self.random_blink()
        self.play_student_changes(
            "confused", "sassy", "erm"
        )
        self.teacher_says(
            """
            If you trust
            the mobius strip 
            fact...
            """,
            target_mode = "guilty",            
            width = 4,
        )
        self.random_blink()

class TryItYourself(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            It's actually an
            edifying exercise.
        """)
        self.random_blink()
        self.play_student_changes(*["pondering"]*3)
        self.random_blink(2)

        pi = self.get_students()[1]
        bubble = pi.get_bubble(
            "thought", 
            width = 4, height = 4,
            direction = RIGHT
        )
        bubble.set_fill(BLACK, opacity = 1)
        bubble.write("Orientation seem\\\\ to matter...")
        self.play(
            FadeIn(bubble),
            Write(bubble.content)
        )
        self.random_blink(3)

class OneMoreAnimation(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            One more animation,
            but first...
        """)
        self.play_student_changes(*["happy"]*3)
        self.random_blink()

class PatreonThanks(Scene):
    CONFIG = {
        "specific_patrons" : [
            "Loo Yu Jun",
            "Tom",
            "Othman Alikhan",
            "Juan Batiz-Benet",
            "Markus Persson",
            "Joseph John Cox",
            "Achille Brighton",
            "Kirk Werklund",
            "Luc Ritchie",
            "Ripta Pasay",
            "PatrickJMT  ",
            "Felipe Diniz",
        ]
    }
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)

        n_patrons = len(self.specific_patrons)
        special_thanks = OldTexText("Special thanks to:")
        special_thanks.set_color(YELLOW)
        special_thanks.shift(2*UP)

        left_patrons = VGroup(*list(map(TexText, 
            self.specific_patrons[:n_patrons/2]
        )))
        right_patrons = VGroup(*list(map(TexText, 
            self.specific_patrons[n_patrons/2:]
        )))
        for patrons, vect in (left_patrons, LEFT), (right_patrons, RIGHT):
            patrons.arrange(DOWN, aligned_edge = LEFT)
            patrons.next_to(special_thanks, DOWN)
            patrons.to_edge(vect, buff = LARGE_BUFF)

        self.play(morty.change_mode, "gracious")
        self.play(Write(special_thanks, run_time = 1))
        self.play(
            Write(left_patrons),
            morty.look_at, left_patrons
        )
        self.play(
            Write(right_patrons),
            morty.look_at, right_patrons
        )
        self.play(Blink(morty))
        for patrons in left_patrons, right_patrons:
            for index in 0, -1:
                self.play(morty.look_at, patrons[index])
                self.wait()

class CreditTWo(Scene):
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)
        morty.to_edge(RIGHT)

        brother = PiCreature(color = GOLD_E)
        brother.next_to(morty, LEFT)
        brother.look_at(morty.eyes)
        
        headphones = Headphones(height = 1)
        headphones.move_to(morty.eyes, aligned_edge = DOWN)
        headphones.shift(0.1*DOWN)

        url = OldTexText("www.audible.com/3b1b")
        url.to_corner(UP+RIGHT, buff = LARGE_BUFF)

        self.add(morty)
        self.play(Blink(morty))
        self.play(
            FadeIn(headphones), 
            Write(url),
            Animation(morty)
        )
        self.play(morty.change_mode, "happy")
        self.wait()
        self.play(Blink(morty))
        self.wait()
        self.play(
            FadeIn(brother),
            morty.look_at, brother.eyes
        )
        self.play(brother.change_mode, "surprised")
        self.play(Blink(brother))
        self.wait()
        self.play(
            morty.look, LEFT,
            brother.change_mode, "happy",
            brother.look, LEFT
        )
        self.play(Blink(morty))
        self.wait()

class CreditThree(Scene):
    def construct(self):
        logo_dot = Dot().to_edge(UP).shift(3*RIGHT)
        randy = Randolph()
        randy.next_to(ORIGIN, DOWN)
        randy.to_edge(LEFT)
        randy.look(RIGHT)
        self.add(randy)
        bubble = randy.get_bubble(width = 2, height = 2)

        domains = VGroup(*list(map(TexText, [
            "visualnumbertheory.com",
            "buymywidgets.com",
            "learnwhatilearn.com",
        ])))
        domains.arrange(DOWN, aligned_edge = LEFT)
        domains.next_to(randy, UP, buff = LARGE_BUFF)
        domains.shift_onto_screen()

        promo_code = OldTexText("Promo code: TOPOLOGY")
        promo_code.shift(3*RIGHT)
        self.add(promo_code)
        whois = OldTexText("Free WHOIS privacy")
        whois.next_to(promo_code, DOWN, buff = LARGE_BUFF)

        self.play(Blink(randy))
        self.play(
            randy.change_mode, "happy",
            randy.look_at, logo_dot
        )
        self.wait()
        self.play(
            ShowCreation(bubble),
            randy.change_mode, "pondering",
            run_time = 2
        )
        self.play(Blink(randy))
        self.play(
            Transform(bubble, VectorizedPoint(randy.get_corner(UP+LEFT))),
            randy.change_mode, "sad"
        )
        self.wait()
        self.play(
            Write(domains, run_time = 5),
            randy.look_at, domains
        )
        self.wait()
        self.play(Blink(randy))
        self.play(
            randy.change_mode, "hooray",
            randy.look_at, logo_dot,
            FadeOut(domains)
        )
        self.wait()
        self.play(
            Write(whois),
            randy.change_mode, "confused",
            randy.look_at, whois
        )
        self.wait(2)
        self.play(randy.change_mode, "sassy")
        self.wait(2)
        self.play(
            randy.change_mode, "happy",
            randy.look_at, logo_dot
        )
        self.play(Blink(randy))
        self.wait()


class ShiftingLoopPairSurface(Scene):
    def construct(self):
        pass

class ThumbnailImage(ClosedLoopScene):
    def construct(self):
        self.add_rect_dots(square = True)
        for dot in self.dots:
            dot.scale(1.5)
        self.add_connecting_lines(cyclic = True)
        self.connecting_lines.set_stroke(width = 10)
        self.loop.add(self.connecting_lines, self.dots)

        title = OldTexText("Unsolved")
        title.scale(2.5)
        title.to_edge(UP)
        title.set_color_by_gradient(YELLOW, MAROON_B)
        self.add(title)
        self.loop.next_to(title, DOWN, buff = MED_SMALL_BUFF)
        self.loop.shift(2*LEFT)











# ===== File: ./_2016/zeta.py =====
from manim_imports_ext import *

import mpmath
mpmath.mp.dps = 7


def zeta(z):
    max_norm = FRAME_X_RADIUS
    try:
        return np.complex(mpmath.zeta(z))
    except:
        return np.complex(max_norm, 0)


def d_zeta(z):
    epsilon = 0.01
    return (zeta(z + epsilon) - zeta(z))/epsilon


class ComplexTransformationScene(Scene):
    def construct(self):
        pass


class ZetaTransformationScene(ComplexTransformationScene):
    CONFIG = {
        "anchor_density" : 35,
        "min_added_anchors" : 10,
        "max_added_anchors" : 300,
        "num_anchors_to_add_per_line" : 75,
        "post_transformation_stroke_width" : 2,
        "default_apply_complex_function_kwargs" : {
            "run_time" : 5,
        },
        "x_min" : 1,
        "x_max" : int(FRAME_X_RADIUS+2),
        "extra_lines_x_min" : -2,
        "extra_lines_x_max" : 4,
        "extra_lines_y_min" : -2,
        "extra_lines_y_max" : 2,
    }
    def prepare_for_transformation(self, mob):
        for line in mob.family_members_with_points():
            #Find point of line cloest to 1 on C
            if not isinstance(line, Line):
                line.insert_n_curves(self.min_added_anchors)
                continue
            p1 = line.get_start()+LEFT
            p2 = line.get_end()+LEFT
            t = (-np.dot(p1, p2-p1))/(get_norm(p2-p1)**2)
            closest_to_one = interpolate(
                line.get_start(), line.get_end(), t
            )
            #See how big this line will become
            diameter = abs(zeta(complex(*closest_to_one[:2])))
            target_num_curves = np.clip(
                int(self.anchor_density*np.pi*diameter),
                self.min_added_anchors,
                self.max_added_anchors,
            )
            num_curves = line.get_num_curves()
            if num_curves < target_num_curves:
                line.insert_n_curves(target_num_curves-num_curves)
            line.make_smooth()

    def add_extra_plane_lines_for_zeta(self, animate = False, **kwargs):
        dense_grid = self.get_dense_grid(**kwargs)
        if animate:
            self.play(ShowCreation(dense_grid))
        self.plane.add(dense_grid)
        self.add(self.plane)

    def get_dense_grid(self, step_size = 1./16):
        epsilon = 0.1
        x_range = np.arange(
            max(self.x_min, self.extra_lines_x_min),
            min(self.x_max, self.extra_lines_x_max),
            step_size
        )
        y_range = np.arange(
            max(self.y_min, self.extra_lines_y_min),
            min(self.y_max, self.extra_lines_y_max),
            step_size
        )
        vert_lines = VGroup(*[
            Line(
                self.y_min*UP,
                self.y_max*UP,
            ).shift(x*RIGHT)
            for x in x_range
            if abs(x-1) > epsilon
        ])
        vert_lines.set_color_by_gradient(
            self.vert_start_color, self.vert_end_color
        )
        horiz_lines = VGroup(*[
            Line(
                self.x_min*RIGHT,
                self.x_max*RIGHT,
            ).shift(y*UP)
            for y in y_range
            if abs(y) > epsilon
        ])
        horiz_lines.set_color_by_gradient(
            self.horiz_start_color, self.horiz_end_color
        )
        dense_grid = VGroup(horiz_lines, vert_lines)
        dense_grid.set_stroke(width = 1)
        return dense_grid

    def add_reflected_plane(self, animate = False):
        reflected_plane = self.get_reflected_plane()
        if animate:
            self.play(ShowCreation(reflected_plane, run_time = 5))
        self.plane.add(reflected_plane)
        self.add(self.plane)

    def get_reflected_plane(self):
        reflected_plane = self.plane.copy()
        reflected_plane.rotate(np.pi, UP, about_point = RIGHT)
        for mob in reflected_plane.family_members_with_points():
            mob.set_color(
                Color(rgb = 1-0.5*color_to_rgb(mob.get_color()))
            )
        self.prepare_for_transformation(reflected_plane)
        reflected_plane.submobjects = list(reversed(
            reflected_plane.family_members_with_points()
        ))
        return reflected_plane

    def apply_zeta_function(self, **kwargs):
        transform_kwargs = dict(self.default_apply_complex_function_kwargs)
        transform_kwargs.update(kwargs)
        self.apply_complex_function(zeta, **kwargs)

class TestZetaOnHalfPlane(ZetaTransformationScene):
    CONFIG = {
        "anchor_density" : 15,
    }
    def construct(self):
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.prepare_for_transformation(self.plane)
        print(sum([
            mob.get_num_points()
            for mob in self.plane.family_members_with_points()
        ]))
        print(len(self.plane.family_members_with_points()))
        self.apply_zeta_function()
        self.wait()

class TestZetaOnFullPlane(ZetaTransformationScene):
    def construct(self):
        self.add_transformable_plane(animate = True)
        self.add_extra_plane_lines_for_zeta(animate = True)
        self.add_reflected_plane(animate = True)
        self.apply_zeta_function()


class TestZetaOnLine(ZetaTransformationScene):
    def construct(self):
        line = Line(UP+20*LEFT, UP+20*RIGHT)
        self.add_transformable_plane()
        self.plane.submobjects = [line]
        self.apply_zeta_function()
        self.wait(2)
        self.play(ShowCreation(line, run_time = 10))
        self.wait(3)

######################

class IntroduceZeta(ZetaTransformationScene):
    CONFIG = {
        "default_apply_complex_function_kwargs" : {
            "run_time" : 8,
        }
    }
    def construct(self):
        title = OldTexText("Riemann zeta function")
        title.add_background_rectangle()
        title.to_corner(UP+LEFT)
        func_mob = VGroup(
            OldTex("\\zeta(s) = "),
            OldTex("\\sum_{n=1}^\\infty \\frac{1}{n^s}")
        )
        func_mob.arrange(RIGHT, buff = 0)
        for submob in func_mob:
            submob.add_background_rectangle()
        func_mob.next_to(title, DOWN)

        randy = Randolph().flip()
        randy.to_corner(DOWN+RIGHT)

        self.add_foreground_mobjects(title, func_mob)
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.play(ShowCreation(self.plane, run_time = 2))
        reflected_plane = self.get_reflected_plane()
        self.play(ShowCreation(reflected_plane, run_time = 2))
        self.plane.add(reflected_plane)
        self.wait()
        self.apply_zeta_function()
        self.wait(2)
        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "confused",
            randy.look_at, func_mob,
        )
        self.play(Blink(randy))
        self.wait()

class WhyPeopleMayKnowIt(TeacherStudentsScene):
    def construct(self):
        title = OldTexText("Riemann zeta function")
        title.to_corner(UP+LEFT)
        func_mob = OldTex(
            "\\zeta(s) = \\sum_{n=1}^\\infty \\frac{1}{n^s}"
        )
        func_mob.next_to(title, DOWN, aligned_edge = LEFT)
        self.add(title, func_mob)

        mercenary_thought = VGroup(
            OldTex("\\$1{,}000{,}000").set_color_by_gradient(GREEN_B, GREEN_D),
            OldTex("\\zeta(s) = 0")
        )
        mercenary_thought.arrange(DOWN)
        divergent_sum = VGroup(
            OldTex("1+2+3+4+\\cdots = -\\frac{1}{12}"),
            OldTex("\\zeta(-1) = -\\frac{1}{12}")
        )
        divergent_sum.arrange(DOWN)
        divergent_sum[0].set_color_by_gradient(YELLOW, MAROON_B)
        divergent_sum[1].set_color(BLACK)

        #Thoughts
        self.play(*it.chain(*[
            [pi.change_mode, "pondering", pi.look_at, func_mob]
            for pi in self.get_pi_creatures()
        ]))
        self.random_blink()
        self.student_thinks(
            mercenary_thought, index = 2,
            target_mode = "surprised",
        )
        student = self.get_students()[2]
        self.random_blink()
        self.wait(2)
        self.student_thinks(
            divergent_sum, index = 1,
            added_anims = [student.change_mode, "plain"]
        )
        student = self.get_students()[1]
        self.play(
            student.change_mode, "confused",
            student.look_at, divergent_sum,
        )
        self.random_blink()
        self.play(*it.chain(*[
            [pi.change_mode, "confused", pi.look_at, divergent_sum]
            for pi in self.get_pi_creatures()
        ]))
        self.wait()
        self.random_blink()
        divergent_sum[1].set_color(WHITE)
        self.play(Write(divergent_sum[1]))
        self.random_blink()
        self.wait()

        #Ask about continuation
        self.student_says(
            OldTexText("Can you explain \\\\" , "``analytic continuation''?"),
            index = 1,
            target_mode = "raise_right_hand"
        )
        self.play_student_changes(
            "raise_left_hand",
            "raise_right_hand",
            "raise_left_hand",
        )
        self.play(
            self.get_teacher().change_mode, "happy",
            self.get_teacher().look_at, student.eyes,
        )
        self.random_blink()
        self.wait(2)
        self.random_blink()
        self.wait()

class ComplexValuedFunctions(ComplexTransformationScene):
    def construct(self):
        title = OldTexText("Complex-valued function")
        title.scale(1.5)
        title.add_background_rectangle()
        title.to_edge(UP)
        self.add(title)

        z_in = Dot(UP+RIGHT, color = YELLOW)
        z_out = Dot(4*RIGHT + 2*UP, color = MAROON_B)
        arrow = Arrow(z_in, z_out, buff = 0.1)
        arrow.set_color(WHITE)
        z = OldTex("z").next_to(z_in, DOWN+LEFT, buff = SMALL_BUFF)
        z.set_color(z_in.get_color())
        f_z = OldTex("f(z)").next_to(z_out, UP+RIGHT, buff = SMALL_BUFF)
        f_z.set_color(z_out.get_color())

        self.add(z_in, z)
        self.wait()
        self.play(ShowCreation(arrow))
        self.play(
            ShowCreation(z_out),
            Write(f_z)
        )
        self.wait(2)

class PreviewZetaAndContinuation(ZetaTransformationScene):
    CONFIG = {
        "default_apply_complex_function_kwargs" : {
            "run_time" : 4,
        }
    }
    def construct(self):
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        reflected_plane = self.get_reflected_plane()

        titles = [
            OldTexText(
                "What does", "%s"%s,
                "look like?",
                alignment = "",
            )
            for s in [
                "$\\displaystyle \\sum_{n=1}^\\infty \\frac{1}{n^s}$",
                "analytic continuation"
            ]
        ]
        for mob in titles:
            mob[1].set_color(YELLOW)
            mob.to_corner(UP+LEFT, buff = 0.7)
            mob.add_background_rectangle()

        self.remove(self.plane)
        self.play(Write(titles[0], run_time = 2))
        self.add_foreground_mobjects(titles[0])
        self.play(FadeIn(self.plane))
        self.apply_zeta_function()
        reflected_plane.apply_complex_function(zeta)
        reflected_plane.make_smooth()
        reflected_plane.set_stroke(width = 2)
        self.wait()
        self.play(Transform(*titles))
        self.wait()
        self.play(ShowCreation(
            reflected_plane,
            lag_ratio = 0,
            run_time = 2
        ))
        self.wait()

class AssumeKnowledgeOfComplexNumbers(ComplexTransformationScene):
    def construct(self):
        z = complex(5, 2)
        dot = Dot(z.real*RIGHT + z.imag*UP, color = YELLOW)
        line = Line(ORIGIN, dot.get_center(), color = dot.get_color())
        x_line = Line(ORIGIN, z.real*RIGHT, color = GREEN_B)
        y_line = Line(ORIGIN, z.imag*UP, color = RED)
        y_line.shift(z.real*RIGHT)
        complex_number_label = OldTex(
            "%d+%di"%(int(z.real), int(z.imag))
        )
        complex_number_label[0].set_color(x_line.get_color())
        complex_number_label[2].set_color(y_line.get_color())
        complex_number_label.next_to(dot, UP)

        text = VGroup(
            OldTexText("Assumed knowledge:"),
            OldTexText("1) What complex numbers are."),
            OldTexText("2) How to work with them."),
            OldTexText("3) Maybe derivatives?"),
        )
        text.arrange(DOWN, aligned_edge = LEFT)
        for words in text:
            words.add_background_rectangle()
        text[0].shift(LEFT)
        text[-1].set_color(PINK)
        text.to_corner(UP+LEFT)

        self.play(Write(text[0]))
        self.wait()
        self.play(FadeIn(text[1]))
        self.play(
            ShowCreation(x_line),
            ShowCreation(y_line),
            ShowCreation(VGroup(line, dot)),
            Write(complex_number_label),
        )
        self.play(Write(text[2]))
        self.wait(2)
        self.play(Write(text[3]))
        self.wait()
        self.play(text[3].fade)

class DefineForRealS(PiCreatureScene):
    def construct(self):
        zeta_def, s_group = self.get_definition("s")

        self.initial_definition(zeta_def)
        self.plug_in_two(zeta_def)
        self.plug_in_three_and_four(zeta_def)
        self.plug_in_negative_values(zeta_def)

    def initial_definition(self, zeta_def):
        zeta_s, sum_terms, brace, sigma = zeta_def

        self.say("Let's define $\\zeta(s)$")
        self.blink()
        pre_zeta_s = VGroup(
            *self.pi_creature.bubble.content.copy()[-4:]
        )
        pre_zeta_s.add(VectorizedPoint(pre_zeta_s.get_right()))
        self.play(
            Transform(pre_zeta_s, zeta_s),
            *self.get_bubble_fade_anims()
        )
        self.remove(pre_zeta_s)
        self.add(zeta_s)
        self.wait()

        for count, term in enumerate(sum_terms):
            self.play(FadeIn(term), run_time = 0.5)
            if count%2 == 0:
                self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(sigma),
            self.pi_creature.change_mode, "pondering"
        )
        self.wait()

    def plug_in_two(self, zeta_def):
        two_def = self.get_definition("2")[0]
        number_line = NumberLine(
            x_min = 0,
            x_max = 3,
            tick_frequency = 0.25,
            big_tick_numbers = list(range(4)),
            unit_size = 3,
        )
        number_line.add_numbers()
        number_line.next_to(self.pi_creature, LEFT)
        number_line.to_edge(LEFT)
        self.number_line = number_line

        lines, braces, dots, pi_dot = self.get_sum_lines(2)
        fracs = VGroup(*[
            OldTex("\\frac{1}{%d}"%((d+1)**2)).scale(0.7)
            for d, brace in enumerate(braces)
        ])
        for frac, brace, line in zip(fracs, braces, lines):
            frac.set_color(line.get_color())
            frac.next_to(brace, UP, buff = SMALL_BUFF)
            if frac is fracs[-1]:
                frac.shift(0.5*RIGHT + 0.2*UP)
                arrow = Arrow(
                    frac.get_bottom(), brace.get_top(),
                    tip_length = 0.1,
                    buff = 0.1
                )
                arrow.set_color(line.get_color())
                frac.add(arrow)

        pi_term = OldTex("= \\frac{\\pi^2}{6}")
        pi_term.next_to(zeta_def[1], RIGHT)
        pi_arrow = Arrow(
            pi_term[-1].get_bottom(), pi_dot,
            color = pi_dot.get_color()
        )
        approx = OldTex("\\approx 1.645")
        approx.next_to(pi_term)

        self.play(Transform(zeta_def, two_def))
        self.wait()
        self.play(ShowCreation(number_line))

        for frac, brace, line in zip(fracs, braces, lines):
            self.play(
                Write(frac),
                GrowFromCenter(brace),
                ShowCreation(line),
                run_time = 0.7
            )
            self.wait(0.7)
        self.wait()
        self.play(
            ShowCreation(VGroup(*lines[4:])),
            Write(dots)
        )
        self.wait()
        self.play(
            Write(pi_term),
            ShowCreation(VGroup(pi_arrow, pi_dot)),
            self.pi_creature.change_mode, "hooray"
        )
        self.wait()
        self.play(
            Write(approx),
            self.pi_creature.change_mode, "happy"
        )
        self.wait(3)
        self.play(*list(map(FadeOut, [
            fracs, pi_arrow, pi_dot, approx,
        ])))
        self.lines = lines
        self.braces = braces
        self.dots = dots
        self.final_dot = pi_dot
        self.final_sum = pi_term

    def plug_in_three_and_four(self, zeta_def):
        final_sums = ["1.202\\dots", "\\frac{\\pi^4}{90}"]
        sum_terms, brace, sigma = zeta_def[1:]
        for exponent, final_sum in zip([3, 4], final_sums):
            self.transition_to_new_input(zeta_def, exponent, final_sum)
            self.wait()

        arrow = Arrow(sum_terms.get_left(), sum_terms.get_right())
        arrow.next_to(sum_terms, DOWN)
        smaller_words = OldTexText("Getting smaller")
        smaller_words.next_to(arrow, DOWN)
        self.arrow, self.smaller_words = arrow, smaller_words

        self.wait()
        self.play(
            ShowCreation(arrow),
            Write(smaller_words)
        )
        self.change_mode("happy")
        self.wait(2)

    def plug_in_negative_values(self, zeta_def):
        zeta_s, sum_terms, brace, sigma = zeta_def
        arrow = self.arrow
        smaller_words = self.smaller_words
        bigger_words = OldTexText("Getting \\emph{bigger}?")
        bigger_words.move_to(self.smaller_words)

        #plug in -1
        self.transition_to_new_input(zeta_def, -1, "-\\frac{1}{12}")
        self.play(
            Transform(self.smaller_words, bigger_words),
            self.pi_creature.change_mode, "confused"
        )
        new_sum_terms = OldTex(
            list("1+2+3+4+") + ["\\cdots"]
        )
        new_sum_terms.move_to(sum_terms, LEFT)
        arrow.target = arrow.copy().next_to(new_sum_terms, DOWN)
        arrow.target.stretch_to_fit_width(new_sum_terms.get_width())
        bigger_words.next_to(arrow.target, DOWN)
        new_brace = Brace(new_sum_terms, UP)
        self.play(
            Transform(sum_terms, new_sum_terms),
            Transform(brace, new_brace),
            sigma.next_to, new_brace, UP,
            MoveToTarget(arrow),
            Transform(smaller_words, bigger_words),
            self.final_sum.next_to, new_sum_terms, RIGHT
        )
        self.wait(3)

        #plug in -2
        new_sum_terms = OldTex(
            list("1+4+9+16+") + ["\\cdots"]
        )
        new_sum_terms.move_to(sum_terms, LEFT)
        new_zeta_def, ignore = self.get_definition("-2")
        zeta_minus_two, ignore, ignore, new_sigma = new_zeta_def
        new_sigma.next_to(brace, UP)
        new_final_sum = OldTex("=0")
        new_final_sum.next_to(new_sum_terms)
        lines, braces, dots, final_dot = self.get_sum_lines(-2)

        self.play(
            Transform(zeta_s, zeta_minus_two),
            Transform(sum_terms, new_sum_terms),
            Transform(sigma, new_sigma),
            Transform(self.final_sum, new_final_sum),
            Transform(self.lines, lines),
            Transform(self.braces, braces),
        )
        self.wait()
        self.change_mode("pleading")
        self.wait(2)

    def get_definition(self, input_string, input_color = YELLOW):
        inputs = VGroup()
        num_shown_terms = 4
        n_input_chars = len(input_string)

        zeta_s_eq = OldTex("\\zeta(%s) = "%input_string)
        zeta_s_eq.to_edge(LEFT, buff = LARGE_BUFF)
        zeta_s_eq.shift(0.5*UP)
        inputs.add(*zeta_s_eq[2:2+n_input_chars])

        sum_terms = OldTex(*it.chain(*list(zip(
            [
                "\\frac{1}{%d^{%s}}"%(d, input_string)
                for d in range(1, 1+num_shown_terms)
            ],
            it.cycle(["+"])
        ))))
        sum_terms.add(OldTex("\\cdots").next_to(sum_terms))
        sum_terms.next_to(zeta_s_eq, RIGHT)
        for x in range(num_shown_terms):
            inputs.add(*sum_terms[2*x][-n_input_chars:])


        brace = Brace(sum_terms, UP)
        sigma = OldTex(
            "\\sum_{n=1}^\\infty \\frac{1}{n^{%s}}"%input_string
        )
        sigma.next_to(brace, UP)
        inputs.add(*sigma[-n_input_chars:])

        inputs.set_color(input_color)
        group = VGroup(zeta_s_eq, sum_terms, brace, sigma)
        return group, inputs

    def get_sum_lines(self, exponent, line_thickness = 6):
        num_lines = 100 if exponent > 0 else 6
        powers = [0] + [x**(-exponent) for x in range(1, num_lines)]
        power_sums = np.cumsum(powers)
        lines = VGroup(*[
            Line(
                self.number_line.number_to_point(s1),
                self.number_line.number_to_point(s2),
            )
            for s1, s2 in zip(power_sums, power_sums[1:])
        ])
        lines.set_stroke(width = line_thickness)
        # VGroup(*lines[:4]).set_color_by_gradient(RED, GREEN_B)
        # VGroup(*lines[4:]).set_color_by_gradient(GREEN_B, MAROON_B)
        VGroup(*lines[::2]).set_color(MAROON_B)
        VGroup(*lines[1::2]).set_color(RED)

        braces = VGroup(*[
            Brace(line, UP)
            for line in lines[:4]
        ])
        dots = OldTex("...")
        dots.stretch_to_fit_width(
            0.8 * VGroup(*lines[4:]).get_width()
        )
        dots.next_to(braces, RIGHT, buff = SMALL_BUFF)

        final_dot = Dot(
            self.number_line.number_to_point(power_sums[-1]),
            color = GREEN_B
        )

        return lines, braces, dots, final_dot

    def transition_to_new_input(self, zeta_def, exponent, final_sum):
        new_zeta_def = self.get_definition(str(exponent))[0]
        lines, braces, dots, final_dot = self.get_sum_lines(exponent)
        final_sum = OldTex("=" + final_sum)
        final_sum.next_to(new_zeta_def[1][-1])
        final_sum.shift(SMALL_BUFF*UP)
        self.play(
            Transform(zeta_def, new_zeta_def),
            Transform(self.lines, lines),
            Transform(self.braces, braces),
            Transform(self.dots, dots),
            Transform(self.final_dot, final_dot),
            Transform(self.final_sum, final_sum),
            self.pi_creature.change_mode, "pondering"
        )

class ReadIntoZetaFunction(Scene):
    CONFIG = {
        "statement" : "$\\zeta(-1) = -\\frac{1}{12}$",
        "target_mode" : "frustrated",
    }
    def construct(self):
        randy = Randolph(mode = "pondering")
        randy.shift(3*LEFT+DOWN)
        paper = Rectangle(width = 4, height = 5)
        paper.next_to(randy, RIGHT, aligned_edge = DOWN)
        paper.set_color(WHITE)
        max_width = 0.8*paper.get_width()

        title = OldTexText("$\\zeta(s)$ manual")
        title.next_to(paper.get_top(), DOWN)
        title.set_color(YELLOW)
        paper.add(title)
        paragraph_lines = VGroup(
            Line(LEFT, RIGHT),
            Line(LEFT, RIGHT).shift(0.2*DOWN),
            Line(LEFT, ORIGIN).shift(0.4*DOWN)
        )
        paragraph_lines.set_width(max_width)
        paragraph_lines.next_to(title, DOWN, MED_LARGE_BUFF)
        paper.add(paragraph_lines)
        max_height = 1.5*paragraph_lines.get_height()

        statement = OldTexText(self.statement)
        if statement.get_width() > max_width:
            statement.set_width(max_width)
        if statement.get_height() > max_height:
            statement.set_height(max_height)

        statement.next_to(paragraph_lines, DOWN)
        statement.set_color(GREEN_B)
        paper.add(paragraph_lines.copy().next_to(statement, DOWN, MED_LARGE_BUFF))

        randy.look_at(statement)
        self.add(randy, paper)
        self.play(Write(statement))
        self.play(
            randy.change_mode, self.target_mode,
            randy.look_at, title
        )
        self.play(Blink(randy))
        self.play(randy.look_at, statement)
        self.wait()

class ReadIntoZetaFunctionTrivialZero(ReadIntoZetaFunction):
    CONFIG = {
        "statement" : "$\\zeta(-2n) = 0$"
    }

class ReadIntoZetaFunctionAnalyticContinuation(ReadIntoZetaFunction):
    CONFIG = {
        "statement" : "...analytic \\\\ continuation...",
        "target_mode" : "confused",
    }

class IgnoreNegatives(TeacherStudentsScene):
    def construct(self):
        definition = OldTex("""
            \\zeta(s) = \\sum_{n=1}^{\\infty} \\frac{1}{n^s}
        """)
        VGroup(definition[2], definition[-1]).set_color(YELLOW)
        definition.to_corner(UP+LEFT)
        self.add(definition)
        brace = Brace(definition, DOWN)
        only_s_gt_1 = brace.get_text("""
            Only defined
            for $s > 1$
        """)
        only_s_gt_1[-3].set_color(YELLOW)


        self.play_student_changes(*["confused"]*3)
        words = OldTexText(
            "Ignore $s \\le 1$ \\dots \\\\",
            "For now."
        )
        words[0][6].set_color(YELLOW)
        words[1].set_color(BLACK)
        self.teacher_says(words)
        self.play(words[1].set_color, WHITE)
        self.play_student_changes(*["happy"]*3)
        self.play(
            GrowFromCenter(brace),
            Write(only_s_gt_1),
            *it.chain(*[
                [pi.look_at, definition]
                for pi in self.get_pi_creatures()
            ])
        )
        self.random_blink(3)

class RiemannFatherOfComplex(ComplexTransformationScene):
    def construct(self):
        name = OldTexText(
            "Bernhard Riemann $\\rightarrow$ Complex analysis"
        )
        name.to_corner(UP+LEFT)
        name.shift(0.25*DOWN)
        name.add_background_rectangle()
        # photo = Square()
        photo = ImageMobject("Riemann", invert = False)
        photo.set_width(5)
        photo.next_to(name, DOWN, aligned_edge = LEFT)


        self.add(photo)
        self.play(Write(name))
        self.wait()

        input_dot = Dot(2*RIGHT+UP, color = YELLOW)
        arc = Arc(-2*np.pi/3)
        arc.rotate(-np.pi)
        arc.add_tip()
        arc.shift(input_dot.get_top()-arc.get_points()[0]+SMALL_BUFF*UP)
        output_dot = Dot(
            arc.get_points()[-1] + SMALL_BUFF*(2*RIGHT+DOWN),
            color = MAROON_B
        )
        for dot, tex in (input_dot, "z"), (output_dot, "f(z)"):
            dot.label = OldTex(tex)
            dot.label.add_background_rectangle()
            dot.label.next_to(dot, DOWN+RIGHT, buff = SMALL_BUFF)
            dot.label.set_color(dot.get_color())

        self.play(
            ShowCreation(input_dot),
            Write(input_dot.label)
        )
        self.play(ShowCreation(arc))
        self.play(
            ShowCreation(output_dot),
            Write(output_dot.label)
        )
        self.wait()

class FromRealToComplex(ComplexTransformationScene):
    CONFIG = {
        "plane_config" : {
            "space_unit_to_x_unit" : 2,
            "space_unit_to_y_unit" : 2,
        },
        "background_label_scale_val" : 0.7,
        "output_color" : GREEN_B,
        "num_lines_in_spiril_sum" : 1000,
    }
    def construct(self):
        self.handle_background()
        self.show_real_to_real()
        self.transition_to_complex()
        self.single_out_complex_exponent()
        ##Fade to several scenes defined below
        self.show_s_equals_two_lines()
        self.transition_to_spiril_sum()
        self.vary_complex_input()
        self.show_domain_of_convergence()
        self.ask_about_visualizing_all()

    def handle_background(self):
        self.remove(self.background)
        #Oh yeah, this is great practice...
        self.background[-1].remove(*self.background[-1][-3:])

    def show_real_to_real(self):
        zeta = self.get_zeta_definition("2",  "\\frac{\\pi^2}{6}")
        number_line = NumberLine(
            unit_size = 2,
            tick_frequency = 0.5,
            big_tick_numbers = list(range(-2, 3))
        )
        number_line.add_numbers()
        input_dot = Dot(number_line.number_to_point(2))
        input_dot.set_color(YELLOW)

        output_dot = Dot(number_line.number_to_point(np.pi**2/6))
        output_dot.set_color(self.output_color)

        arc = Arc(
            2*np.pi/3, start_angle = np.pi/6,
        )
        arc.stretch_to_fit_width(
            (input_dot.get_center()-output_dot.get_center())[0]
        )
        arc.stretch_to_fit_height(0.5)
        arc.next_to(input_dot.get_center(), UP, aligned_edge = RIGHT)
        arc.add_tip()

        two = zeta[1][2].copy()
        sum_term = zeta[-1]
        self.add(number_line, *zeta[:-1])
        self.wait()
        self.play(Transform(two, input_dot))
        self.remove(two)
        self.add(input_dot)
        self.play(ShowCreation(arc))
        self.play(ShowCreation(output_dot))
        self.play(Transform(output_dot.copy(), sum_term))
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(sum_term)
        self.wait(2)
        self.play(
            ShowCreation(
                self.background,
                run_time = 2
            ),
            FadeOut(VGroup(arc, output_dot, number_line)),
            Animation(zeta),
            Animation(input_dot)
        )
        self.wait(2)

        self.zeta = zeta
        self.input_dot = input_dot

    def transition_to_complex(self):
        complex_zeta = self.get_zeta_definition("2+i", "???")
        input_dot = self.input_dot
        input_dot.generate_target()
        input_dot.target.move_to(
            self.background.num_pair_to_point((2, 1))
        )
        input_label = OldTex("2+i")
        input_label.set_color(YELLOW)
        input_label.next_to(input_dot.target, DOWN+RIGHT, buff = SMALL_BUFF)
        input_label.add_background_rectangle()
        input_label.save_state()
        input_label.replace(VGroup(*complex_zeta[1][2:5]))
        input_label.background_rectangle.scale(0.01)
        self.input_label = input_label

        self.play(Transform(self.zeta, complex_zeta))
        self.wait()
        self.play(
            input_label.restore,
            MoveToTarget(input_dot)
        )
        self.wait(2)

    def single_out_complex_exponent(self):
        frac_scale_factor = 1.2

        randy = Randolph()
        randy.to_corner()
        bubble = randy.get_bubble(height = 4)
        bubble.set_fill(BLACK, opacity = 1)

        frac = VGroup(
            VectorizedPoint(self.zeta[2][3].get_left()),
            self.zeta[2][3],
            VectorizedPoint(self.zeta[2][3].get_right()),
            self.zeta[2][4],
        ).copy()
        frac.generate_target()
        frac.target.scale(frac_scale_factor)
        bubble.add_content(frac.target)
        new_frac = OldTex(
            "\\Big(", "\\frac{1}{2}", "\\Big)", "^{2+i}"
        )
        new_frac[-1].set_color(YELLOW)
        new_frac.scale(frac_scale_factor)
        new_frac.move_to(frac.target)
        new_frac.shift(LEFT+0.2*UP)

        words = OldTexText("Not repeated \\\\", " multiplication")
        words.scale(0.8)
        words.set_color(RED)
        words.next_to(new_frac, RIGHT)

        new_words = OldTexText("Not \\emph{super} \\\\", "crucial to know...")
        new_words.replace(words)
        new_words.scale(1.3)

        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "confused",
            randy.look_at, bubble,
            ShowCreation(bubble),
            MoveToTarget(frac)
        )
        self.play(Blink(randy))
        self.play(Transform(frac, new_frac))
        self.play(Write(words))
        for x in range(2):
            self.wait(2)
            self.play(Blink(randy))
        self.play(
            Transform(words, new_words),
            randy.change_mode, "maybe"
        )
        self.wait()
        self.play(Blink(randy))
        self.play(randy.change_mode, "happy")
        self.wait()
        self.play(*list(map(FadeOut, [randy, bubble, frac, words])))

    def show_s_equals_two_lines(self):
        self.input_label.save_state()
        zeta = self.get_zeta_definition("2", "\\frac{\\pi^2}{6}")
        lines, output_dot = self.get_sum_lines(2)
        sum_terms = self.zeta[2][:-1:3]
        dots_copy = zeta[2][-1].copy()
        pi_copy = zeta[3].copy()
        def transform_and_replace(m1, m2):
            self.play(Transform(m1, m2))
            self.remove(m1)
            self.add(m2)

        self.play(
            self.input_dot.shift, 2*DOWN,
            self.input_label.fade, 0.7,
        )
        self.play(Transform(self.zeta, zeta))

        for term, line in zip(sum_terms, lines):
            line.save_state()
            line.next_to(term, DOWN)
            term_copy = term.copy()
            transform_and_replace(term_copy, line)
            self.play(line.restore)
        later_lines = VGroup(*lines[4:])
        transform_and_replace(dots_copy, later_lines)
        self.wait()
        transform_and_replace(pi_copy, output_dot)
        self.wait()

        self.lines = lines
        self.output_dot = output_dot

    def transition_to_spiril_sum(self):
        zeta = self.get_zeta_definition("2+i", "1.15 - 0.44i")
        zeta.set_width(FRAME_WIDTH-1)
        zeta.to_corner(UP+LEFT)
        lines, output_dot = self.get_sum_lines(complex(2, 1))

        self.play(
            self.input_dot.shift, 2*UP,
            self.input_label.restore,
        )
        self.wait()
        self.play(Transform(self.zeta, zeta))
        self.wait()
        self.play(
            Transform(self.lines, lines),
            Transform(self.output_dot, output_dot),
            run_time = 2,
            path_arc = -np.pi/6,
        )
        self.wait()

    def vary_complex_input(self):
        zeta = self.get_zeta_definition("s", "")
        zeta[3].set_color(BLACK)
        self.play(Transform(self.zeta, zeta))
        self.play(FadeOut(self.input_label))
        self.wait(2)
        inputs = [
            complex(1.5, 1.8),
            complex(1.5, -1),
            complex(3, -1),
            complex(1.5, 1.8),
            complex(1.5, -1.8),
            complex(1.4, -1.8),
            complex(1.5, 0),
            complex(2, 1),
        ]
        for s in inputs:
            input_point = self.z_to_point(s)
            lines, output_dot = self.get_sum_lines(s)
            self.play(
                self.input_dot.move_to, input_point,
                Transform(self.lines, lines),
                Transform(self.output_dot, output_dot),
                run_time = 2
            )
            self.wait()
        self.wait()

    def show_domain_of_convergence(self, opacity = 0.2):
        domain = Rectangle(
            width = FRAME_X_RADIUS-2,
            height = FRAME_HEIGHT,
            stroke_width = 0,
            fill_color = YELLOW,
            fill_opacity = opacity,
        )
        domain.to_edge(RIGHT, buff = 0)
        anti_domain = Rectangle(
            width = FRAME_X_RADIUS+2,
            height = FRAME_HEIGHT,
            stroke_width = 0,
            fill_color = RED,
            fill_opacity = opacity,
        )
        anti_domain.to_edge(LEFT, buff = 0)

        domain_words = OldTexText("""
            $\\zeta(s)$ happily
            converges and
            makes sense
        """)
        domain_words.to_corner(UP+RIGHT, buff = MED_LARGE_BUFF)

        anti_domain_words = OldTexText("""
            Not so much...
        """)
        anti_domain_words.next_to(ORIGIN, LEFT, buff = LARGE_BUFF)
        anti_domain_words.shift(1.5*DOWN)

        self.play(FadeIn(domain))
        self.play(Write(domain_words))
        self.wait()
        self.play(FadeIn(anti_domain))
        self.play(Write(anti_domain_words))
        self.wait(2)
        self.play(*list(map(FadeOut, [
            anti_domain, anti_domain_words,
        ])))
        self.domain_words = domain_words

    def ask_about_visualizing_all(self):
        morty = Mortimer().flip()
        morty.scale(0.7)
        morty.to_corner(DOWN+LEFT)
        bubble = morty.get_bubble(SpeechBubble, height = 4)
        bubble.set_fill(BLACK, opacity = 0.5)
        bubble.write("""
            How can we visualize
            this for all inputs?
        """)

        self.play(FadeIn(morty))
        self.play(
            morty.change_mode, "speaking",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(morty))
        self.wait(3)
        self.play(
            morty.change_mode, "pondering",
            morty.look_at, self.input_dot,
            *list(map(FadeOut, [
                bubble, bubble.content, self.domain_words
            ]))
        )
        arrow = Arrow(self.input_dot, self.output_dot, buff = SMALL_BUFF)
        arrow.set_color(WHITE)
        self.play(ShowCreation(arrow))
        self.play(Blink(morty))
        self.wait()

    def get_zeta_definition(self, input_string, output_string, input_color = YELLOW):
        inputs = VGroup()
        num_shown_terms = 4
        n_input_chars = len(input_string)

        zeta_s_eq = OldTex("\\zeta(%s) = "%input_string)
        zeta_s_eq.to_edge(LEFT, buff = LARGE_BUFF)
        zeta_s_eq.shift(0.5*UP)
        inputs.add(*zeta_s_eq[2:2+n_input_chars])


        raw_sum_terms = OldTex(*[
            "\\frac{1}{%d^{%s}} + "%(d, input_string)
            for d in range(1, 1+num_shown_terms)
        ])
        sum_terms = VGroup(*it.chain(*[
            [
                VGroup(*term[:3]),
                VGroup(*term[3:-1]),
                term[-1],
            ]
            for term in raw_sum_terms
        ]))
        sum_terms.add(OldTex("\\cdots").next_to(sum_terms[-1]))
        sum_terms.next_to(zeta_s_eq, RIGHT)
        for x in range(num_shown_terms):
            inputs.add(*sum_terms[3*x+1])

        output = OldTex("= \\," + output_string)
        output.next_to(sum_terms, RIGHT)
        output.set_color(self.output_color)

        inputs.set_color(input_color)
        group = VGroup(zeta_s_eq, sum_terms, output)
        group.to_edge(UP)
        group.add_to_back(BackgroundRectangle(group))
        return group

    def get_sum_lines(self, exponent, line_thickness = 6):
        powers = [0] + [
            x**(-exponent)
            for x in range(1, self.num_lines_in_spiril_sum)
        ]
        power_sums = np.cumsum(powers)
        lines = VGroup(*[
            Line(*list(map(self.z_to_point, z_pair)))
            for z_pair in zip(power_sums, power_sums[1:])
        ])
        widths = np.linspace(line_thickness, 0, len(list(lines)))
        for line, width in zip(lines, widths):
            line.set_stroke(width = width)
        VGroup(*lines[::2]).set_color(MAROON_B)
        VGroup(*lines[1::2]).set_color(RED)

        final_dot = Dot(
            # self.z_to_point(power_sums[-1]),
            self.z_to_point(zeta(exponent)),
            color = self.output_color
        )

        return lines, final_dot

class TerritoryOfExponents(ComplexTransformationScene):
    def construct(self):
        self.add_title()
        familiar_territory = OldTexText("Familiar territory")
        familiar_territory.set_color(YELLOW)
        familiar_territory.next_to(ORIGIN, UP+RIGHT)
        familiar_territory.shift(2*UP)
        real_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        real_line.set_color(YELLOW)
        arrow1 = Arrow(familiar_territory.get_bottom(), real_line.get_left())
        arrow2 = Arrow(familiar_territory.get_bottom(), real_line.get_right())
        VGroup(arrow1, arrow2).set_color(WHITE)

        extended_realm = OldTexText("Extended realm")
        extended_realm.move_to(familiar_territory)
        full_plane = Rectangle(
            width = FRAME_WIDTH,
            height = FRAME_HEIGHT,
            fill_color = YELLOW,
            fill_opacity = 0.3
        )

        self.add(familiar_territory)
        self.play(ShowCreation(arrow1))
        self.play(
            Transform(arrow1, arrow2),
            ShowCreation(real_line)
        )
        self.play(FadeOut(arrow1))
        self.play(
            FadeIn(full_plane),
            Transform(familiar_territory, extended_realm),
            Animation(real_line)
        )

    def add_title(self):
        exponent = OldTex(
            "\\left(\\frac{1}{2}\\right)^s"
        )
        exponent[-1].set_color(YELLOW)
        exponent.next_to(ORIGIN, LEFT, MED_LARGE_BUFF).to_edge(UP)
        self.add_foreground_mobjects(exponent)

class ComplexExponentiation(Scene):
    def construct(self):
        self.extract_pure_imaginary_part()
        self.add_on_planes()
        self.show_imaginary_powers()

    def extract_pure_imaginary_part(self):
        original = OldTex(
            "\\left(\\frac{1}{2}\\right)", "^{2+i}"
        )
        split = OldTex(
             "\\left(\\frac{1}{2}\\right)", "^{2}",
             "\\left(\\frac{1}{2}\\right)", "^{i}",
        )
        VGroup(original[-1], split[1], split[3]).set_color(YELLOW)
        VGroup(original, split).shift(UP)
        real_part = VGroup(*split[:2])
        imag_part = VGroup(*split[2:])

        brace = Brace(real_part)
        we_understand = brace.get_text(
            "We understand this"
        )
        VGroup(brace, we_understand).set_color(GREEN_B)

        self.add(original)
        self.wait()
        self.play(*[
            Transform(*pair)
            for pair in [
                (original[0], split[0]),
                (original[1][0], split[1]),
                (original[0].copy(), split[2]),
                (VGroup(*original[1][1:]), split[3]),
            ]
        ])
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(real_part, imag_part)
        self.wait()
        self.play(
            GrowFromCenter(brace),
            FadeIn(we_understand),
            real_part.set_color, GREEN_B
        )
        self.wait()
        self.play(
            imag_part.move_to, imag_part.get_left(),
            *list(map(FadeOut, [brace, we_understand, real_part]))
        )
        self.wait()
        self.imag_exponent = imag_part

    def add_on_planes(self):
        left_plane = NumberPlane(x_radius = (FRAME_X_RADIUS-1)/2)
        left_plane.to_edge(LEFT, buff = 0)
        imag_line = Line(DOWN, UP).scale(FRAME_Y_RADIUS)
        imag_line.set_color(YELLOW).fade(0.3)
        imag_line.move_to(left_plane.get_center())
        left_plane.add(imag_line)
        left_title = OldTexText("Input space")
        left_title.add_background_rectangle()
        left_title.set_color(YELLOW)
        left_title.next_to(left_plane.get_top(), DOWN)

        right_plane = NumberPlane(x_radius = (FRAME_X_RADIUS-1)/2)
        right_plane.to_edge(RIGHT, buff = 0)
        unit_circle = Circle()
        unit_circle.set_color(MAROON_B).fade(0.3)
        unit_circle.shift(right_plane.get_center())
        right_plane.add(unit_circle)
        right_title = OldTexText("Output space")
        right_title.add_background_rectangle()
        right_title.set_color(MAROON_B)
        right_title.next_to(right_plane.get_top(), DOWN)

        for plane in left_plane, right_plane:
            labels = VGroup()
            for x in range(-2, 3):
                label = OldTex(str(x))
                label.move_to(plane.num_pair_to_point((x, 0)))
                labels.add(label)
            for y in range(-3, 4):
                if y == 0:
                    continue
                label = OldTex(str(y) + "i")
                label.move_to(plane.num_pair_to_point((0, y)))
                labels.add(label)
            for label in labels:
                label.scale(0.5)
                label.next_to(
                    label.get_center(), DOWN+RIGHT,
                    buff = SMALL_BUFF
                )
            plane.add(labels)

        arrow = Arrow(LEFT, RIGHT)

        self.play(
            ShowCreation(left_plane),
            Write(left_title),
            run_time = 3
        )
        self.play(
            ShowCreation(right_plane),
            Write(right_title),
            run_time = 3
        )
        self.play(ShowCreation(arrow))
        self.wait()
        self.left_plane = left_plane
        self.right_plane = right_plane

    def show_imaginary_powers(self):
        i = complex(0, 1)
        input_dot = Dot(self.z_to_point(i))
        input_dot.set_color(YELLOW)
        output_dot = Dot(self.z_to_point(0.5**(i), is_input = False))
        output_dot.set_color(MAROON_B)

        output_dot.save_state()
        output_dot.move_to(input_dot)
        output_dot.set_color(input_dot.get_color())

        curr_base = 0.5
        def output_dot_update(ouput_dot):
            y = input_dot.get_center()[1]
            output_dot.move_to(self.z_to_point(
                curr_base**complex(0, y), is_input = False
            ))
            return output_dot

        def walk_up_and_down():
            for vect in 3*DOWN, 5*UP, 5*DOWN, 2*UP:
                self.play(
                    input_dot.shift, vect,
                    UpdateFromFunc(output_dot, output_dot_update),
                    run_time = 3
                )

        exp = self.imag_exponent[-1]
        new_exp = OldTex("ti")
        new_exp.set_color(exp.get_color())
        new_exp.set_height(exp.get_height())
        new_exp.move_to(exp, LEFT)

        nine = OldTex("9")
        nine.set_color(BLUE)
        denom = self.imag_exponent[0][3]
        denom.save_state()
        nine.replace(denom)

        self.play(Transform(exp, new_exp))
        self.play(input_dot.shift, 2*UP)
        self.play(input_dot.shift, 2*DOWN)
        self.wait()
        self.play(output_dot.restore)
        self.wait()
        walk_up_and_down()
        self.wait()
        curr_base = 1./9
        self.play(Transform(denom, nine))
        walk_up_and_down()
        self.wait()

    def z_to_point(self, z, is_input = True):
        if is_input:
            plane = self.left_plane
        else:
            plane = self.right_plane
        return plane.num_pair_to_point((z.real, z.imag))

class SizeAndRotationBreakdown(Scene):
    def construct(self):
        original = OldTex(
            "\\left(\\frac{1}{2}\\right)", "^{2+i}"
        )
        split = OldTex(
             "\\left(\\frac{1}{2}\\right)", "^{2}",
             "\\left(\\frac{1}{2}\\right)", "^{i}",
        )
        VGroup(original[-1], split[1], split[3]).set_color(YELLOW)
        VGroup(original, split).shift(UP)
        real_part = VGroup(*split[:2])
        imag_part = VGroup(*split[2:])

        size_brace = Brace(real_part)
        size = size_brace.get_text("Size")
        rotation_brace = Brace(imag_part, UP)
        rotation = rotation_brace.get_text("Rotation")

        self.add(original)
        self.wait()
        self.play(*[
            Transform(*pair)
            for pair in [
                (original[0], split[0]),
                (original[1][0], split[1]),
                (original[0].copy(), split[2]),
                (VGroup(*original[1][1:]), split[3]),
            ]
        ])
        self.play(
            GrowFromCenter(size_brace),
            Write(size)
        )
        self.play(
            GrowFromCenter(rotation_brace),
            Write(rotation)
        )
        self.wait()

class SeeLinksInDescription(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            See links in the
            description for more.
        """)
        self.play(*it.chain(*[
            [pi.change_mode, "hooray", pi.look, DOWN]
            for pi in self.get_students()
        ]))
        self.random_blink(3)

class ShowMultiplicationOfRealAndImaginaryExponentialParts(FromRealToComplex):
    def construct(self):
        self.break_up_exponent()
        self.show_multiplication()

    def break_up_exponent(self):
        original = OldTex(
            "\\left(\\frac{1}{2}\\right)", "^{2+i}"
        )
        split = OldTex(
             "\\left(\\frac{1}{2}\\right)", "^{2}",
             "\\left(\\frac{1}{2}\\right)", "^{i}",
        )
        VGroup(original[-1], split[1], split[3]).set_color(YELLOW)
        VGroup(original, split).to_corner(UP+LEFT)
        rect = BackgroundRectangle(split)
        real_part = VGroup(*split[:2])
        imag_part = VGroup(*split[2:])

        self.add(rect, original)
        self.wait()
        self.play(*[
            Transform(*pair)
            for pair in [
                (original[0], split[0]),
                (original[1][0], split[1]),
                (original[0].copy(), split[2]),
                (VGroup(*original[1][1:]), split[3]),
            ]
        ])
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(real_part, imag_part)
        self.wait()
        self.real_part = real_part
        self.imag_part = imag_part

    def show_multiplication(self):
        real_part = self.real_part.copy()
        imag_part = self.imag_part.copy()
        for part in real_part, imag_part:
            part.add_to_back(BackgroundRectangle(part))

        fourth_point = self.z_to_point(0.25)
        fourth_line = Line(ORIGIN, fourth_point)
        brace = Brace(fourth_line, UP, buff = SMALL_BUFF)
        fourth_dot = Dot(fourth_point)
        fourth_group = VGroup(fourth_line, brace, fourth_dot)
        fourth_group.set_color(RED)

        circle = Circle(radius = 2, color = MAROON_B)
        circle.fade(0.3)
        imag_power_point = self.z_to_point(0.5**complex(0, 1))
        imag_power_dot = Dot(imag_power_point)
        imag_power_line = Line(ORIGIN, imag_power_point)
        VGroup(imag_power_dot, imag_power_line).set_color(MAROON_B)

        full_power_tex = OldTex(
            "\\left(\\frac{1}{2}\\right)", "^{2+i}"
        )
        full_power_tex[-1].set_color(YELLOW)
        full_power_tex.add_background_rectangle()
        full_power_tex.scale(0.7)
        full_power_tex.next_to(
            0.5*self.z_to_point(0.5**complex(2, 1)),
            UP+RIGHT
        )

        self.play(
            real_part.scale, 0.7,
            real_part.next_to, brace, UP, SMALL_BUFF, LEFT,
            ShowCreation(fourth_dot)
        )
        self.play(
            GrowFromCenter(brace),
            ShowCreation(fourth_line),
        )
        self.wait()
        self.play(
            imag_part.scale, 0.7,
            imag_part.next_to, imag_power_dot, DOWN+RIGHT, SMALL_BUFF,
            ShowCreation(imag_power_dot)
        )
        self.play(ShowCreation(circle), Animation(imag_power_dot))
        self.play(ShowCreation(imag_power_line))
        self.wait(2)
        self.play(
            fourth_group.rotate, imag_power_line.get_angle()
        )
        real_part.generate_target()
        imag_part.generate_target()
        real_part.target.next_to(brace, UP+RIGHT, buff = 0)
        imag_part.target.next_to(real_part.target, buff = 0)
        self.play(*list(map(MoveToTarget, [real_part, imag_part])))
        self.wait()

class ComplexFunctionsAsTransformations(ComplexTransformationScene):
    def construct(self):
        self.add_title()
        input_dots, output_dots, arrows = self.get_dots()

        self.play(FadeIn(
            input_dots,
            run_time = 2,
            lag_ratio = 0.5
        ))
        for in_dot, out_dot, arrow in zip(input_dots, output_dots, arrows):
            self.play(
                Transform(in_dot.copy(), out_dot),
                ShowCreation(arrow)
            )
            self.wait()
        self.wait()


    def add_title(self):
        title = OldTexText("Complex functions as transformations")
        title.add_background_rectangle()
        title.to_edge(UP)
        self.add(title)

    def get_dots(self):
        input_points = [
            RIGHT+2*UP,
            4*RIGHT+DOWN,
            2*LEFT+2*UP,
            LEFT+DOWN,
            6*LEFT+DOWN,
        ]
        output_nudges = [
            DOWN+RIGHT,
            2*UP+RIGHT,
            2*RIGHT+2*DOWN,
            2*RIGHT+DOWN,
            RIGHT+2*UP,
        ]
        input_dots = VGroup(*list(map(Dot, input_points)))
        input_dots.set_color(YELLOW)
        output_dots = VGroup(*[
            Dot(ip + on)
            for ip, on in zip(input_points, output_nudges)
        ])
        output_dots.set_color(MAROON_B)
        arrows = VGroup(*[
            Arrow(in_dot, out_dot, buff = 0.1, color = WHITE)
            for in_dot, out_dot, in zip(input_dots, output_dots)
        ])
        for i, dot in enumerate(input_dots):
            label = OldTex("s_%d"%i)
            label.set_color(dot.get_color())
            label.next_to(dot, DOWN+LEFT, buff = SMALL_BUFF)
            dot.add(label)
        for i, dot in enumerate(output_dots):
            label = OldTex("f(s_%d)"%i)
            label.set_color(dot.get_color())
            label.next_to(dot, UP+RIGHT, buff = SMALL_BUFF)
            dot.add(label)
        return input_dots, output_dots, arrows

class VisualizingSSquared(ComplexTransformationScene):
    CONFIG = {
        "num_anchors_to_add_per_line" : 100,
        "horiz_end_color" : GOLD,
        "y_min" : 0,
    }
    def construct(self):
        self.add_title()
        self.plug_in_specific_values()
        self.show_transformation()
        self.comment_on_two_dimensions()

    def add_title(self):
        title = OldTex("f(", "s", ") = ", "s", "^2")
        title.set_color_by_tex("s", YELLOW)
        title.add_background_rectangle()
        title.scale(1.5)
        title.to_corner(UP+LEFT)
        self.play(Write(title))
        self.add_foreground_mobject(title)
        self.wait()
        self.title = title

    def plug_in_specific_values(self):
        inputs = list(map(complex, [2, -1, complex(0, 1)]))
        input_dots  = VGroup(*[
            Dot(self.z_to_point(z), color = YELLOW)
            for z in inputs
        ])
        output_dots = VGroup(*[
            Dot(self.z_to_point(z**2), color = BLUE)
            for z in inputs
        ])
        arrows = VGroup()
        VGroup(*[
            ParametricCurve(
                lambda t : self.z_to_point(z**(1.1+0.8*t))
            )
            for z in inputs
        ])
        for z, dot in zip(inputs, input_dots):
            path = ParametricCurve(
                lambda t : self.z_to_point(z**(1+t))
            )
            dot.path = path
            arrow = ParametricCurve(
                lambda t : self.z_to_point(z**(1.1+0.8*t))
            )
            stand_in_arrow = Arrow(
                arrow.get_points()[-2], arrow.get_points()[-1],
                tip_length = 0.2
            )
            arrow.add(stand_in_arrow.tip)
            arrows.add(arrow)
        arrows.set_color(WHITE)

        for input_dot, output_dot, arrow in zip(input_dots, output_dots, arrows):
            input_dot.save_state()
            input_dot.move_to(self.title[1][1])
            input_dot.set_fill(opacity = 0)

            self.play(input_dot.restore)
            self.wait()
            self.play(ShowCreation(arrow))
            self.play(ShowCreation(output_dot))
            self.wait()
        self.add_foreground_mobjects(arrows, output_dots, input_dots)
        self.input_dots = input_dots
        self.output_dots = output_dots

    def add_transformable_plane(self, **kwargs):
        ComplexTransformationScene.add_transformable_plane(self, **kwargs)
        self.plane.next_to(ORIGIN, UP, buff = 0.01)
        self.plane.add(self.plane.copy().rotate(np.pi, RIGHT))
        self.plane.add(
            Line(ORIGIN, FRAME_X_RADIUS*RIGHT, color = self.horiz_end_color),
            Line(ORIGIN, FRAME_X_RADIUS*LEFT, color = self.horiz_end_color),
        )
        self.add(self.plane)

    def show_transformation(self):
        self.add_transformable_plane()
        self.play(ShowCreation(self.plane, run_time = 3))

        self.wait()
        self.apply_complex_homotopy(
            lambda z, t : z**(1+t),
            added_anims = [
                MoveAlongPath(dot, dot.path, run_time = 5)
                for dot in self.input_dots
            ],
            run_time = 5
        )
        self.wait(2)


    def comment_on_two_dimensions(self):
        morty = Mortimer().flip()
        morty.scale(0.7)
        morty.to_corner(DOWN+LEFT)
        bubble = morty.get_bubble(SpeechBubble, height = 2, width = 4)
        bubble.set_fill(BLACK, opacity = 0.9)
        bubble.write("""
            It all happens
            in two dimensions!
        """)
        self.foreground_mobjects = []

        self.play(FadeIn(morty))
        self.play(
            morty.change_mode, "hooray",
            ShowCreation(bubble),
            Write(bubble.content),
        )
        self.play(Blink(morty))
        self.wait(2)

class ShowZetaOnHalfPlane(ZetaTransformationScene):
    CONFIG = {
        "x_min" : 1,
        "x_max" : int(FRAME_X_RADIUS+2),
    }
    def construct(self):
        self.add_title()
        self.initial_transformation()
        self.react_to_transformation()
        self.show_cutoff()
        self.set_color_i_line()
        self.show_continuation()
        self.emphsize_sum_doesnt_make_sense()


    def add_title(self):
        zeta = OldTex(
            "\\zeta(", "s", ")=",
            *[
                "\\frac{1}{%d^s} + "%d
                for d in range(1, 5)
            ] + ["\\cdots"]
        )
        zeta[1].set_color(YELLOW)
        for mob in zeta[3:3+4]:
            mob[-2].set_color(YELLOW)
        zeta.add_background_rectangle()
        zeta.scale(0.8)
        zeta.to_corner(UP+LEFT)
        self.add_foreground_mobjects(zeta)
        self.zeta = zeta

    def initial_transformation(self):
        self.add_transformable_plane()
        self.wait()
        self.add_extra_plane_lines_for_zeta(animate = True)
        self.wait(2)
        self.plane.save_state()
        self.apply_zeta_function()
        self.wait(2)

    def react_to_transformation(self):
        morty = Mortimer().flip()
        morty.to_corner(DOWN+LEFT)
        bubble = morty.get_bubble(SpeechBubble)
        bubble.set_fill(BLACK, 0.5)
        bubble.write("\\emph{Damn}!")
        bubble.resize_to_content()
        bubble.pin_to(morty)

        self.play(FadeIn(morty))
        self.play(
            morty.change_mode, "surprised",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(morty))
        self.play(morty.look_at, self.plane.get_top())
        self.wait()
        self.play(
            morty.look_at, self.plane.get_bottom(),
            *list(map(FadeOut, [bubble, bubble.content]))
        )
        self.play(Blink(morty))
        self.play(FadeOut(morty))

    def show_cutoff(self):
        words = OldTexText("Such an abrupt stop...")
        words.add_background_rectangle()
        words.next_to(ORIGIN, UP+LEFT)
        words.shift(LEFT+UP)

        line = Line(*list(map(self.z_to_point, [
            complex(np.euler_gamma, u*FRAME_Y_RADIUS)
            for u in (1, -1)
        ])))
        line.set_color(YELLOW)
        arrows = [
            Arrow(words.get_right(), point)
            for point in line.get_start_and_end()
        ]

        self.play(Write(words, run_time = 2))
        self.play(ShowCreation(arrows[0]))
        self.play(
            Transform(*arrows),
            ShowCreation(line),
            run_time = 2
        )
        self.play(FadeOut(arrows[0]))
        self.wait(2)
        self.play(*list(map(FadeOut, [words, line])))

    def set_color_i_line(self):
        right_i_lines, left_i_lines = [
            VGroup(*[
                Line(
                    vert_vect+RIGHT,
                    vert_vect+(FRAME_X_RADIUS+1)*horiz_vect
                )
                for vert_vect in (UP, DOWN)
            ])
            for horiz_vect in (RIGHT, LEFT)
        ]
        right_i_lines.set_color(YELLOW)
        left_i_lines.set_color(BLUE)
        for lines in right_i_lines, left_i_lines:
            self.prepare_for_transformation(lines)

        self.restore_mobjects(self.plane)
        self.plane.add(*right_i_lines)
        colored_plane = self.plane.copy()
        right_i_lines.set_stroke(width = 0)
        self.play(
            self.plane.set_stroke, GREY, 1,
        )
        right_i_lines.set_stroke(YELLOW, width = 3)
        self.play(ShowCreation(right_i_lines))
        self.plane.save_state()
        self.wait(2)
        self.apply_zeta_function()
        self.wait(2)

        left_i_lines.save_state()
        left_i_lines.apply_complex_function(zeta)
        self.play(ShowCreation(left_i_lines, run_time = 5))
        self.wait()
        self.restore_mobjects(self.plane, left_i_lines)
        self.play(Transform(self.plane, colored_plane))
        self.wait()
        self.left_i_lines = left_i_lines

    def show_continuation(self):
        reflected_plane = self.get_reflected_plane()
        self.play(ShowCreation(reflected_plane, run_time = 2))
        self.plane.add(reflected_plane)
        self.remove(self.left_i_lines)
        self.wait()
        self.apply_zeta_function()
        self.wait(2)
        self.play(ShowCreation(
            reflected_plane,
            run_time = 6,
            rate_func = lambda t : 1-there_and_back(t)
        ))
        self.wait(2)

    def emphsize_sum_doesnt_make_sense(self):
        brace = Brace(VGroup(*self.zeta[1][3:]))
        words = brace.get_text("""
            Still fails to converge
            when Re$(s) < 1$
        """, buff = SMALL_BUFF)
        words.add_background_rectangle()
        words.scale(0.8)
        divergent_sum = OldTex("1+2+3+4+\\cdots")
        divergent_sum.next_to(ORIGIN, UP)
        divergent_sum.to_edge(LEFT)
        divergent_sum.add_background_rectangle()

        self.play(
            GrowFromCenter(brace),
            Write(words)
        )
        self.wait(2)
        self.play(Write(divergent_sum))
        self.wait(2)

    def restore_mobjects(self, *mobjects):
        self.play(*it.chain(*[
            [m.restore, m.make_smooth]
            for m in  mobjects
        ]), run_time = 2)
        for m in mobjects:
            self.remove(m)
            m.restore()
            self.add(m)

class ShowConditionalDefinition(Scene):
    def construct(self):
        zeta = OldTex("\\zeta(s)=")
        zeta[2].set_color(YELLOW)
        sigma = OldTex("\\sum_{n=1}^\\infty \\frac{1}{n^s}")
        sigma[-1].set_color(YELLOW)
        something_else = OldTexText("Something else...")
        conditions = VGroup(*[
            OldTexText("if Re$(s) %s 1$"%s)
            for s in (">", "\\le")
        ])
        definitions = VGroup(sigma, something_else)
        definitions.arrange(DOWN, buff = MED_LARGE_BUFF, aligned_edge = LEFT)
        conditions.arrange(DOWN, buff = LARGE_BUFF)
        definitions.shift(2*LEFT+2*UP)
        conditions.next_to(definitions, RIGHT, buff = LARGE_BUFF, aligned_edge = DOWN)
        brace = Brace(definitions, LEFT)
        zeta.next_to(brace, LEFT)

        sigma.save_state()
        sigma.next_to(zeta)
        self.add(zeta, sigma)
        self.wait()
        self.play(
            sigma.restore,
            GrowFromCenter(brace),
            FadeIn(something_else)
        )
        self.play(Write(conditions))
        self.wait()

        underbrace = Brace(something_else)
        question = underbrace.get_text("""
            What to put here?
        """)
        VGroup(underbrace, question).set_color(GREEN_B)

        self.play(
            GrowFromCenter(underbrace),
            Write(question),
            something_else.set_color, GREEN_B
        )
        self.wait(2)

class SquiggleOnExtensions(ZetaTransformationScene):
    CONFIG = {
        "x_min" : 1,
        "x_max" : int(FRAME_X_RADIUS+2),
    }
    def construct(self):
        self.show_negative_one()
        self.cycle_through_options()
        self.lock_into_place()

    def show_negative_one(self):
        self.add_transformable_plane()
        thin_plane = self.plane.copy()
        thin_plane.add(self.get_reflected_plane())
        self.remove(self.plane)
        self.add_extra_plane_lines_for_zeta()
        reflected_plane = self.get_reflected_plane()
        self.plane.add(reflected_plane)
        self.remove(self.plane)
        self.add(thin_plane)

        dot = self.note_point(-1, "-1")
        self.play(
            ShowCreation(self.plane, run_time = 2),
            Animation(dot),
            run_time = 2
        )
        self.remove(thin_plane)
        self.apply_zeta_function(added_anims = [
            ApplyMethod(
                dot.move_to, self.z_to_point(-1./12),
                run_time = 5
            )
        ])
        dot_to_remove = self.note_point(-1./12, "-\\frac{1}{12}")
        self.remove(dot_to_remove)
        self.left_plane = reflected_plane
        self.dot = dot

    def note_point(self, z, label_tex):
        dot = Dot(self.z_to_point(z))
        dot.set_color(YELLOW)
        label = OldTex(label_tex)
        label.add_background_rectangle()
        label.next_to(dot, UP+LEFT, buff = SMALL_BUFF)
        label.shift(LEFT)
        arrow = Arrow(label.get_right(), dot, buff = SMALL_BUFF)

        self.play(Write(label, run_time = 1))
        self.play(*list(map(ShowCreation, [arrow, dot])))
        self.wait()
        self.play(*list(map(FadeOut, [arrow, label])))
        return dot

    def cycle_through_options(self):
        gamma = np.euler_gamma
        def shear(point):
            x, y, z = point
            return np.array([
                x,
                y+0.25*(1-x)**2,
                0
            ])
        def mixed_scalar_func(point):
            x, y, z = point
            scalar = 1 + (gamma-x)/(gamma+FRAME_X_RADIUS)
            return np.array([
                (scalar**2)*x,
                (scalar**3)*y,
                0
            ])
        def alt_mixed_scalar_func(point):
            x, y, z = point
            scalar = 1 + (gamma-x)/(gamma+FRAME_X_RADIUS)
            return np.array([
                (scalar**5)*x,
                (scalar**2)*y,
                0
            ])
        def sinusoidal_func(point):
            x, y, z = point
            freq = np.pi/gamma
            return np.array([
                x-0.2*np.sin(x*freq)*np.sin(y),
                y-0.2*np.sin(x*freq)*np.sin(y),
                0
            ])
        funcs = [
            shear,
            mixed_scalar_func,
            alt_mixed_scalar_func,
            sinusoidal_func,
        ]
        for mob in self.left_plane.family_members_with_points():
            if np.all(np.abs(mob.get_points()[:,1]) < 0.1):
                self.left_plane.remove(mob)

        new_left_planes = [
            self.left_plane.copy().apply_function(func)
            for func in funcs
        ]
        new_dots = [
            self.dot.copy().move_to(func(self.dot.get_center()))
            for func in funcs
        ]
        self.left_plane.save_state()
        for plane, dot in zip(new_left_planes, new_dots):
            self.play(
                Transform(self.left_plane, plane),
                Transform(self.dot, dot),
                run_time = 3
            )
            self.wait()
        self.play(FadeOut(self.dot))

        #Squiggle on example
        self.wait()
        self.play(FadeOut(self.left_plane))
        self.play(ShowCreation(
            self.left_plane,
            run_time = 5,
            rate_func=linear
        ))
        self.wait()

    def lock_into_place(self):
        words = OldTexText(
            """Only one extension
            has a """,
            "\\emph{derivative}",
            "everywhere",
            alignment = ""
        )
        words.to_corner(UP+LEFT)
        words.set_color_by_tex("\\emph{derivative}", YELLOW)
        words.add_background_rectangle()

        self.play(Write(words))
        self.add_foreground_mobjects(words)
        self.play(self.left_plane.restore)
        self.wait()

class DontKnowDerivatives(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            """
            You said we don't
            need derivatives!
            """,
            target_mode = "pleading"
        )
        self.random_blink(2)
        self.student_says(
            """
            I get $\\frac{df}{dx}$, just not
            for complex functions
            """,
            target_mode = "confused",
            index = 2
        )
        self.random_blink(2)
        self.teacher_says(
            """
            Luckily, there's a purely
            geometric intuition here.
            """,
            target_mode = "hooray"
        )
        self.play_student_changes(*["happy"]*3)
        self.random_blink(3)

class IntroduceAnglePreservation(VisualizingSSquared):
    CONFIG = {
        "num_anchors_to_add_per_line" : 50,
        "use_homotopy" : True,
    }
    def construct(self):
        self.add_title()
        self.show_initial_transformation()
        self.talk_about_derivative()
        self.cycle_through_line_pairs()
        self.note_grid_lines()
        self.name_analytic()

    def add_title(self):
        title = OldTex("f(", "s", ")=", "s", "^2")
        title.set_color_by_tex("s", YELLOW)
        title.scale(1.5)
        title.to_corner(UP+LEFT)
        title.add_background_rectangle()
        self.title = title

        self.add_transformable_plane()
        self.play(Write(title))
        self.add_foreground_mobjects(title)
        self.wait()

    def show_initial_transformation(self):
        self.apply_function()
        self.wait(2)
        self.reset()

    def talk_about_derivative(self):
        randy = Randolph().scale(0.8)
        randy.to_corner(DOWN+LEFT)
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        randy.make_eye_contact(morty)
        for pi, words in (randy, "$f'(s) = 2s$"), (morty, "Here's some \\\\ related geometry..."):
            pi.bubble = pi.get_bubble(SpeechBubble)
            pi.bubble.set_fill(BLACK, opacity = 0.7)
            pi.bubble.write(words)
            pi.bubble.resize_to_content()
            pi.bubble.pin_to(pi)
        for index in 3, 7:
            randy.bubble.content[index].set_color(YELLOW)

        self.play(*list(map(FadeIn, [randy, morty])))
        self.play(
            randy.change_mode, "speaking",
            ShowCreation(randy.bubble),
            Write(randy.bubble.content)
        )
        self.play(Blink(morty))
        self.wait()
        self.play(
            morty.change_mode, "speaking",
            randy.change_mode, "pondering",
            ShowCreation(morty.bubble),
            Write(morty.bubble.content),
        )
        self.play(Blink(randy))
        self.wait()
        self.play(*list(map(FadeOut, [
            randy, morty,
            randy.bubble, randy.bubble.content,
            morty.bubble, morty.bubble.content,
        ])))


    def cycle_through_line_pairs(self):
        line_pairs = [
            (
                Line(3*DOWN+3*RIGHT, 2*UP),
                Line(DOWN+RIGHT, 3*UP+4*RIGHT)
            ),
            (
                Line(RIGHT+3.5*DOWN, RIGHT+2.5*UP),
                Line(3*LEFT+0.5*UP, 3*RIGHT+0.5*UP),
            ),
            (
                Line(4*RIGHT+4*DOWN, RIGHT+2*UP),
                Line(4*DOWN+RIGHT, 2*UP+2*RIGHT)
            ),
        ]
        for lines in line_pairs:
            self.show_angle_preservation_between_lines(*lines)
            self.reset()

    def note_grid_lines(self):
        intersection_inputs = [
            complex(x, y)
            for x in np.arange(-5, 5, 0.5)
            for y in np.arange(0, 3, 0.5)
            if not (x <= 0 and y == 0)
        ]
        brackets = VGroup(*list(map(
            self.get_right_angle_bracket,
            intersection_inputs
        )))
        self.apply_function()
        self.wait()
        self.play(
            ShowCreation(brackets, run_time = 5),
            Animation(self.plane)
        )
        self.wait()

    def name_analytic(self):
        equiv = OldTexText("``Analytic'' $\\Leftrightarrow$ Angle-preserving")
        kind_of = OldTexText("...kind of")
        for text in equiv, kind_of:
            text.scale(1.2)
            text.add_background_rectangle()
        equiv.set_color(YELLOW)
        kind_of.set_color(RED)
        kind_of.next_to(equiv, RIGHT)
        VGroup(equiv, kind_of).next_to(ORIGIN, UP, buff = 1)

        self.play(Write(equiv))
        self.wait(2)
        self.play(Write(kind_of, run_time = 1))
        self.wait(2)

    def reset(self, faded = True):
        self.play(FadeOut(self.plane))
        self.add_transformable_plane()
        if faded:
            self.plane.fade()
        self.play(FadeIn(self.plane))

    def apply_function(self, **kwargs):
        if self.use_homotopy:
            self.apply_complex_homotopy(
                lambda z, t : z**(1+t),
                run_time = 5,
                **kwargs
            )
        else:
            self.apply_complex_function(
                lambda z : z**2,
                **kwargs
            )

    def show_angle_preservation_between_lines(self, *lines):
        R2_endpoints = [
            [l.get_start()[:2], l.get_end()[:2]]
            for l in lines
        ]
        R2_intersection_point = intersection(*R2_endpoints)
        intersection_point = np.array(list(R2_intersection_point) + [0])

        angle1, angle2 = [l.get_angle() for l in lines]
        arc = Arc(
            start_angle = angle1,
            angle = angle2-angle1,
            radius = 0.4,
            color = YELLOW
        )
        arc.shift(intersection_point)
        arc.insert_n_curves(10)
        arc.generate_target()
        input_z = complex(*arc.get_center()[:2])
        scale_factor = abs(2*input_z)
        arc.target.scale_about_point(1./scale_factor, intersection_point)
        arc.target.apply_complex_function(lambda z : z**2)

        angle_tex = OldTex(
            "%d^\\circ"%abs(int((angle2-angle1)*180/np.pi))
        )
        angle_tex.set_color(arc.get_color())
        angle_tex.add_background_rectangle()
        self.put_angle_tex_next_to_arc(angle_tex, arc)
        angle_arrow = Arrow(
            angle_tex, arc,
            color = arc.get_color(),
            buff = 0.1,
        )
        angle_group = VGroup(angle_tex, angle_arrow)


        self.play(*list(map(ShowCreation, lines)))
        self.play(
            Write(angle_tex),
            ShowCreation(angle_arrow),
            ShowCreation(arc)
        )
        self.wait()

        self.play(FadeOut(angle_group))
        self.plane.add(*lines)
        self.apply_function(added_anims = [
            MoveToTarget(arc, run_time = 5)
        ])
        self.put_angle_tex_next_to_arc(angle_tex, arc)
        arrow = Arrow(angle_tex, arc, buff = 0.1)
        arrow.set_color(arc.get_color())
        self.play(
            Write(angle_tex),
            ShowCreation(arrow)
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [arc, angle_tex, arrow])))

    def put_angle_tex_next_to_arc(self, angle_tex, arc):
        vect = arc.point_from_proportion(0.5)-interpolate(
            arc.get_points()[0], arc.get_points()[-1], 0.5
        )
        unit_vect = vect/get_norm(vect)
        angle_tex.move_to(arc.get_center() + 1.7*unit_vect)

    def get_right_angle_bracket(self, input_z):
        output_z = input_z**2
        derivative = 2*input_z
        rotation = np.log(derivative).imag

        brackets = VGroup(
            Line(RIGHT, RIGHT+UP),
            Line(RIGHT+UP, UP)
        )
        brackets.scale(0.15)
        brackets.set_stroke(width = 2)
        brackets.set_color(YELLOW)
        brackets.shift(0.02*UP) ##Why???
        brackets.rotate(rotation, about_point = ORIGIN)
        brackets.shift(self.z_to_point(output_z))
        return brackets

class AngleAtZeroDerivativePoints(IntroduceAnglePreservation):
    CONFIG = {
        "use_homotopy" : True
    }
    def construct(self):
        self.add_title()
        self.is_before_transformation = True
        self.add_transformable_plane()
        self.plane.fade()
        line = Line(3*LEFT+0.5*UP, 3*RIGHT+0.5*DOWN)
        self.show_angle_preservation_between_lines(
            line, line.copy().rotate(np.pi/5)
        )
        self.wait()

    def add_title(self):
        title = OldTex("f(", "s", ")=", "s", "^2")
        title.set_color_by_tex("s", YELLOW)
        title.scale(1.5)
        title.to_corner(UP+LEFT)
        title.add_background_rectangle()
        derivative = OldTex("f'(0) = 0")
        derivative.set_color(RED)
        derivative.scale(1.2)
        derivative.add_background_rectangle()
        derivative.next_to(title, DOWN)

        self.add_foreground_mobjects(title, derivative)


    def put_angle_tex_next_to_arc(self, angle_tex, arc):
        IntroduceAnglePreservation.put_angle_tex_next_to_arc(
            self, angle_tex, arc
        )
        if not self.is_before_transformation:
            two_dot = OldTex("2 \\times ")
            two_dot.set_color(angle_tex.get_color())
            two_dot.next_to(angle_tex, LEFT, buff = SMALL_BUFF)
            two_dot.add_background_rectangle()
            center = angle_tex.get_center()
            angle_tex.add_to_back(two_dot)
            angle_tex.move_to(center)
        else:
            self.is_before_transformation = False

class AnglePreservationAtAnyPairOfPoints(IntroduceAnglePreservation):
    def construct(self):
        self.add_transformable_plane()
        self.plane.fade()
        line_pairs = self.get_line_pairs()
        line_pair = line_pairs[0]
        for target_pair in line_pairs[1:]:
            self.play(Transform(
                line_pair, target_pair,
                run_time = 2,
                path_arc = np.pi
            ))
            self.wait()
        self.show_angle_preservation_between_lines(*line_pair)
        self.show_example_analytic_functions()

    def get_line_pairs(self):
        return list(it.starmap(VGroup, [
            (
                Line(3*DOWN, 3*LEFT+2*UP),
                Line(2*LEFT+DOWN, 3*UP+RIGHT)
            ),
            (
                Line(2*RIGHT+DOWN, 3*LEFT+2*UP),
                Line(LEFT+3*DOWN, 4*RIGHT+3*UP),
            ),
            (
                Line(LEFT+3*DOWN, LEFT+3*UP),
                Line(5*LEFT+UP, 3*RIGHT+UP)
            ),
            (
                Line(4*RIGHT+3*DOWN, RIGHT+2*UP),
                Line(3*DOWN+RIGHT, 2*UP+2*RIGHT)
            ),
        ]))

    def show_example_analytic_functions(self):
        words = OldTexText("Examples of analytic functions:")
        words.shift(2*UP)
        words.set_color(YELLOW)
        words.add_background_rectangle()
        words.next_to(UP, UP).to_edge(LEFT)
        functions = OldTexText(
            "$e^x$, ",
            "$\\sin(x)$, ",
            "any polynomial, "
            "$\\log(x)$, ",
            "\\dots",
        )
        functions.next_to(ORIGIN, UP).to_edge(LEFT)
        for function in functions:
            function.add_to_back(BackgroundRectangle(function))

        self.play(Write(words))
        for function in functions:
            self.play(FadeIn(function))
        self.wait()

class NoteZetaFunctionAnalyticOnRightHalf(ZetaTransformationScene):
    CONFIG = {
        "anchor_density" : 35,
    }
    def construct(self):
        self.add_title()
        self.add_transformable_plane(animate = False)
        self.add_extra_plane_lines_for_zeta(animate = True)
        self.apply_zeta_function()
        self.note_right_angles()

    def add_title(self):
        title = OldTex(
            "\\zeta(s) = \\sum_{n=1}^\\infty \\frac{1}{n^s}"
        )
        title[2].set_color(YELLOW)
        title[-1].set_color(YELLOW)
        title.add_background_rectangle()
        title.to_corner(UP+LEFT)
        self.add_foreground_mobjects(title)

    def note_right_angles(self):
        intersection_inputs = [
            complex(x, y)
            for x in np.arange(1+2./16, 1.4, 1./16)
            for y in np.arange(-0.5, 0.5, 1./16)
            if abs(y) > 1./16
        ]
        brackets = VGroup(*list(map(
            self.get_right_angle_bracket,
            intersection_inputs
        )))
        self.play(ShowCreation(brackets, run_time = 3))
        self.wait()

    def get_right_angle_bracket(self, input_z):
        output_z = zeta(input_z)
        derivative = d_zeta(input_z)
        rotation = np.log(derivative).imag

        brackets = VGroup(
            Line(RIGHT, RIGHT+UP),
            Line(RIGHT+UP, UP)
        )
        brackets.scale(0.1)
        brackets.set_stroke(width = 2)
        brackets.set_color(YELLOW)
        brackets.rotate(rotation, about_point = ORIGIN)
        brackets.shift(self.z_to_point(output_z))
        return brackets

class InfiniteContinuousJigsawPuzzle(ZetaTransformationScene):
    CONFIG = {
        "anchor_density" : 35,
    }
    def construct(self):
        self.set_stage()
        self.add_title()
        self.show_jigsaw()
        self.name_analytic_continuation()

    def set_stage(self):
        self.plane = self.get_dense_grid()
        left_plane = self.get_reflected_plane()
        self.plane.add(left_plane)
        self.apply_zeta_function(run_time = 0)
        self.remove(left_plane)
        lines_per_piece = 5
        pieces = [
            VGroup(*left_plane[lines_per_piece*i:lines_per_piece*(i+1)])
            for i in range(len(list(left_plane))/lines_per_piece)
        ]
        random.shuffle(pieces)
        self.pieces = pieces

    def add_title(self):
        title = OldTexText("Infinite ", "continuous ", "jigsaw puzzle")
        title.scale(1.5)
        title.to_edge(UP)
        for word in title:
            word.add_to_back(BackgroundRectangle(word))
            self.play(FadeIn(word))
        self.wait()
        self.add_foreground_mobjects(title)
        self.title = title

    def show_jigsaw(self):
        for piece in self.pieces:
            self.play(FadeIn(piece, run_time = 0.5))
        self.wait()

    def name_analytic_continuation(self):
        words = OldTexText("``Analytic continuation''")
        words.set_color(YELLOW)
        words.scale(1.5)
        words.next_to(self.title, DOWN, buff = LARGE_BUFF)
        words.add_background_rectangle()
        self.play(Write(words))
        self.wait()

class ThatsHowZetaIsDefined(TeacherStudentsScene):
    def construct(self):
        self.add_zeta_definition()
        self.teacher_says("""
            So that's how
            $\\zeta(s)$ is defined
        """)
        self.play_student_changes(*["hooray"]*3)
        self.random_blink(2)

    def add_zeta_definition(self):
        zeta = OldTex(
            "\\zeta(s) = \\sum_{n=1}^\\infty \\frac{1}{n^s}"
        )
        VGroup(zeta[2], zeta[-1]).set_color(YELLOW)
        zeta.to_corner(UP+LEFT)
        self.add(zeta)

class ManyIntersectingLinesPreZeta(ZetaTransformationScene):
    CONFIG = {
        "apply_zeta" : False,
        "lines_center" : RIGHT,
        "nudge_size" : 0.9,
        "function" : zeta,
        "angle" : np.pi/5,
        "arc_scale_factor" : 0.3,
        "shift_directions" : [LEFT, RIGHT],
    }
    def construct(self):
        self.establish_plane()
        self.add_title()

        line = Line(DOWN+2*LEFT, UP+2*RIGHT)
        lines = VGroup(line, line.copy().rotate(self.angle))
        arc = Arc(start_angle = line.get_angle(), angle = self.angle)
        arc.scale(self.arc_scale_factor)
        arc.set_color(YELLOW)
        lines.add(arc)
        # lines.set_stroke(WHITE, width = 5)
        lines.shift(self.lines_center + self.nudge_size*RIGHT)

        if self.apply_zeta:
            self.apply_zeta_function(run_time = 0)
            lines.set_stroke(width = 0)

        added_anims = self.get_modified_line_anims(lines)
        for vect in self.shift_directions:
            self.play(
                ApplyMethod(lines.shift, 2*self.nudge_size*vect, path_arc = np.pi),
                *added_anims,
                run_time = 3
            )

    def establish_plane(self):
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.add_reflected_plane()
        self.plane.fade()


    def add_title(self):
        if self.apply_zeta:
            title = OldTexText("After \\\\ transformation")
        else:
            title = OldTexText("Before \\\\ transformation")
        title.add_background_rectangle()
        title.to_edge(UP)
        self.add_foreground_mobjects(title)

    def get_modified_line_anims(self, lines):
        return []

class ManyIntersectingLinesPostZeta(ManyIntersectingLinesPreZeta):
    CONFIG = {
        "apply_zeta" : True,
        # "anchor_density" : 5
    }
    def get_modified_line_anims(self, lines):
        n_inserted_points = 30
        new_lines = lines.copy()
        new_lines.set_stroke(width = 5)
        def update_new_lines(lines_to_update):
            transformed = lines.copy()
            self.prepare_for_transformation(transformed)
            transformed.apply_complex_function(self.function)
            transformed.make_smooth()
            transformed.set_stroke(width = 5)
            for start, end in zip(lines_to_update, transformed):
                if start.get_num_points() > 0:
                    start.points = np.array(end.points)
        return [UpdateFromFunc(new_lines, update_new_lines)]

class ManyIntersectingLinesPreSSquared(ManyIntersectingLinesPreZeta):
    CONFIG = {
        "x_min" : -int(FRAME_X_RADIUS),
        "apply_zeta" : False,
        "lines_center" : ORIGIN,
        "nudge_size" : 0.9,
        "function" : lambda z : z**2,
        "shift_directions" : [LEFT, RIGHT, UP, DOWN, DOWN+LEFT, UP+RIGHT],
    }
    def establish_plane(self):
        self.add_transformable_plane()
        self.plane.fade()

    def apply_zeta_function(self, **kwargs):
        self.apply_complex_function(self.function, **kwargs)

class ManyIntersectingLinesPostSSquared(ManyIntersectingLinesPreSSquared):
    CONFIG = {
        "apply_zeta" : True,
    }
    def get_modified_line_anims(self, lines):
        n_inserted_points = 30
        new_lines = lines.copy()
        new_lines.set_stroke(width = 5)
        def update_new_lines(lines_to_update):
            transformed = lines.copy()
            self.prepare_for_transformation(transformed)
            transformed.apply_complex_function(self.function)
            transformed.make_smooth()
            transformed.set_stroke(width = 5)
            for start, end in zip(lines_to_update, transformed):
                if start.get_num_points() > 0:
                    start.points = np.array(end.points)
        return [UpdateFromFunc(new_lines, update_new_lines)]

class ButWhatIsTheExensions(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            """
            But what exactly \\emph{is}
            that continuation?
            """,
            target_mode = "sassy"
        )
        self.play_student_changes("confused", "sassy", "confused")
        self.random_blink(2)
        self.teacher_says("""
            You're $\\$1{,}000{,}000$ richer
            if you can answer
            that fully
        """, target_mode = "shruggie")
        self.play_student_changes(*["pondering"]*3)
        self.random_blink(3)

class MathematiciansLookingAtFunctionEquation(Scene):
    def construct(self):
        equation = OldTex(
            "\\zeta(s)",
            "= 2^s \\pi ^{s-1}",
            "\\sin\\left(\\frac{\\pi s}{2}\\right)",
            "\\Gamma(1-s)",
            "\\zeta(1-s)",
        )
        equation.shift(UP)

        mathy = Mathematician().to_corner(DOWN+LEFT)
        mathys = VGroup(mathy)
        for x in range(2):
            mathys.add(Mathematician().next_to(mathys))
        for mathy in mathys:
            mathy.change_mode("pondering")
            mathy.look_at(equation)

        self.add(mathys)
        self.play(Write(VGroup(*equation[:-1])))
        self.play(Transform(
            equation[0].copy(),
            equation[-1],
            path_arc = -np.pi/3,
            run_time = 2
        ))
        for mathy in mathys:
            self.play(Blink(mathy))
        self.wait()

class DiscussZeros(ZetaTransformationScene):
    def construct(self):
        self.establish_plane()
        self.ask_about_zeros()
        self.show_trivial_zeros()
        self.show_critical_strip()
        self.transform_bit_of_critical_line()
        self.extend_transformed_critical_line()

    def establish_plane(self):
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.add_reflected_plane()
        self.plane.fade()

    def ask_about_zeros(self):
        dots = VGroup(*[
            Dot(
                (2+np.sin(12*alpha))*\
                rotate_vector(RIGHT, alpha+nudge)
            )
            for alpha in np.arange(3*np.pi/20, 2*np.pi, 2*np.pi/5)
            for nudge in [random.random()*np.pi/6]
        ])
        dots.set_color(YELLOW)
        q_marks = VGroup(*[
            OldTex("?").next_to(dot, UP)
            for dot in dots
        ])
        arrows = VGroup(*[
            Arrow(dot, ORIGIN, buff = 0.2, tip_length = 0.1)
            for dot in dots
        ])
        question = OldTexText("Which numbers go to $0$?")
        question.add_background_rectangle()
        question.to_edge(UP)

        for mob in dots, arrows, q_marks:
            self.play(ShowCreation(mob))
        self.play(Write(question))
        self.wait(2)
        dots.generate_target()
        for i, dot in enumerate(dots.target):
            dot.move_to(2*(i+1)*LEFT)
        self.play(
            FadeOut(arrows),
            FadeOut(q_marks),
            FadeOut(question),
            MoveToTarget(dots),
        )
        self.wait()
        self.dots = dots

    def show_trivial_zeros(self):
        trivial_zero_words = OldTexText("``Trivial'' zeros")
        trivial_zero_words.next_to(ORIGIN, UP)
        trivial_zero_words.to_edge(LEFT)

        randy = Randolph().flip()
        randy.to_corner(DOWN+RIGHT)
        bubble = randy.get_bubble()
        bubble.set_fill(BLACK, opacity = 0.8)
        bubble.write("$1^1 + 2^2 + 3^2 + \\cdots = 0$")
        bubble.resize_to_content()
        bubble.pin_to(randy)

        self.plane.save_state()
        self.dots.save_state()
        for dot in self.dots.target:
            dot.move_to(ORIGIN)
        self.apply_zeta_function(
            added_anims = [MoveToTarget(self.dots, run_time = 3)],
            run_time = 3
        )
        self.wait(3)
        self.play(
            self.plane.restore,
            self.plane.make_smooth,
            self.dots.restore,
            run_time = 2
        )
        self.remove(*self.get_mobjects_from_last_animation())
        self.plane.restore()
        self.dots.restore()
        self.add(self.plane, self.dots)

        self.play(Write(trivial_zero_words))
        self.wait()
        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "confused",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(randy))
        self.wait()
        self.play(Blink(randy))
        self.play(*list(map(FadeOut, [
            randy, bubble, bubble.content, trivial_zero_words
        ])))

    def show_critical_strip(self):
        strip = Rectangle(
            height = FRAME_HEIGHT,
            width = 1
        )
        strip.next_to(ORIGIN, RIGHT, buff = 0)
        strip.set_stroke(width = 0)
        strip.set_fill(YELLOW, opacity = 0.3)
        name = OldTexText("Critical strip")
        name.add_background_rectangle()
        name.next_to(ORIGIN, LEFT)
        name.to_edge(UP)
        arrow = Arrow(name.get_bottom(), 0.5*RIGHT+UP)
        primes = OldTex("2, 3, 5, 7, 11, 13, 17, \\dots")
        primes.to_corner(UP+RIGHT)
        # photo = Square()
        photo = ImageMobject("Riemann", invert = False)
        photo.set_width(5)
        photo.to_corner(UP+LEFT)
        new_dots = VGroup(*[
            Dot(0.5*RIGHT + y*UP)
            for y in np.linspace(-2.5, 3.2, 5)
        ])
        new_dots.set_color(YELLOW)
        critical_line = Line(
            0.5*RIGHT+FRAME_Y_RADIUS*DOWN,
            0.5*RIGHT+FRAME_Y_RADIUS*UP,
            color = YELLOW
        )

        self.give_dots_wandering_anims()

        self.play(FadeIn(strip), *self.get_dot_wandering_anims())
        self.play(
            Write(name, run_time = 1),
            ShowCreation(arrow),
            *self.get_dot_wandering_anims()
        )
        self.play(*self.get_dot_wandering_anims())
        self.play(
            FadeIn(primes),
            *self.get_dot_wandering_anims()
        )
        for x in range(7):
            self.play(*self.get_dot_wandering_anims())
        self.play(
            GrowFromCenter(photo),
            FadeOut(name),
            FadeOut(arrow),
            *self.get_dot_wandering_anims()
        )
        self.play(Transform(self.dots, new_dots))
        self.play(ShowCreation(critical_line))
        self.wait(3)
        self.play(
            photo.shift, 7*LEFT,
            *list(map(FadeOut, [
            primes, self.dots, strip
            ]))
        )
        self.remove(photo)
        self.critical_line = critical_line

    def give_dots_wandering_anims(self):
        def func(t):
            result = (np.sin(6*2*np.pi*t) + 1)*RIGHT/2
            result += 3*np.cos(2*2*np.pi*t)*UP
            return result

        self.wandering_path = ParametricCurve(func)
        for i, dot in enumerate(self.dots):
            dot.target = dot.copy()
            q_mark = OldTex("?")
            q_mark.next_to(dot.target, UP)
            dot.target.add(q_mark)
            dot.target.move_to(self.wandering_path.point_from_proportion(
                (float(2+2*i)/(4*len(list(self.dots))))%1
            ))
        self.dot_anim_count = 0

    def get_dot_wandering_anims(self):
        self.dot_anim_count += 1
        if self.dot_anim_count == 1:
            return list(map(MoveToTarget, self.dots))
        denom = 4*(len(list(self.dots)))
        def get_rate_func(index):
            return lambda t : (float(self.dot_anim_count + 2*index + t)/denom)%1
        return [
            MoveAlongPath(
                dot, self.wandering_path,
                rate_func = get_rate_func(i)
            )
            for i, dot in enumerate(self.dots)
        ]

    def transform_bit_of_critical_line(self):
        self.play(
            self.plane.scale, 0.8,
            self.critical_line.scale, 0.8,
            rate_func = there_and_back,
            run_time = 2
        )
        self.wait()
        self.play(
            self.plane.set_stroke, GREY, 1,
            Animation(self.critical_line)
        )
        self.plane.add(self.critical_line)
        self.apply_zeta_function()
        self.wait(2)
        self.play(
            self.plane.fade,
            Animation(self.critical_line)
        )

    def extend_transformed_critical_line(self):
        def func(t):
            z = zeta(complex(0.5, t))
            return z.real*RIGHT + z.imag*UP
        full_line = VGroup(*[
            ParametricCurve(func, t_min = t0, t_max = t0+1)
            for t0 in range(100)
        ])
        full_line.set_color_by_gradient(
            YELLOW, BLUE, GREEN, RED, YELLOW, BLUE, GREEN, RED,
        )
        self.play(ShowCreation(full_line, run_time = 20, rate_func=linear))
        self.wait()

class AskAboutRelationToPrimes(TeacherStudentsScene):
    def construct(self):
        self.student_says("""
            Whoa!  Where the heck
            do primes come in here?
        """, target_mode = "confused")
        self.random_blink(3)
        self.teacher_says("""
            Perhaps in a
            different video.
        """, target_mode = "hesitant")
        self.random_blink(3)

class HighlightCriticalLineAgain(DiscussZeros):
    def construct(self):
        self.establish_plane()
        title = OldTex("\\zeta(", "s", ") = 0")
        title.set_color_by_tex("s", YELLOW)
        title.add_background_rectangle()
        title.to_corner(UP+LEFT)
        self.add(title)

        strip = Rectangle(
            height = FRAME_HEIGHT,
            width = 1
        )
        strip.next_to(ORIGIN, RIGHT, buff = 0)
        strip.set_stroke(width = 0)
        strip.set_fill(YELLOW, opacity = 0.3)
        line = Line(
            0.5*RIGHT+FRAME_Y_RADIUS*UP,
            0.5*RIGHT+FRAME_Y_RADIUS*DOWN,
            color = YELLOW
        )
        randy = Randolph().to_corner(DOWN+LEFT)
        million = OldTex("\\$1{,}000{,}000")
        million.set_color(GREEN_B)
        million.next_to(ORIGIN, UP+LEFT)
        million.shift(2*LEFT)
        arrow1 = Arrow(million.get_right(), line.get_top())
        arrow2 = Arrow(million.get_right(), line.get_bottom())

        self.add(randy, strip)
        self.play(Write(million))
        self.play(
            randy.change_mode, "pondering",
            randy.look_at, line.get_top(),
            ShowCreation(arrow1),
            run_time = 3
        )
        self.play(
            randy.look_at, line.get_bottom(),
            ShowCreation(line),
            Transform(arrow1, arrow2)
        )
        self.play(FadeOut(arrow1))
        self.play(Blink(randy))
        self.wait()
        self.play(randy.look_at, line.get_center())
        self.play(randy.change_mode, "confused")
        self.play(Blink(randy))
        self.wait()
        self.play(randy.change_mode, "pondering")
        self.wait()

class DiscussSumOfNaturals(Scene):
    def construct(self):
        title = OldTex(
            "\\zeta(s) = \\sum_{n=1}^\\infty \\frac{1}{n^s}"
        )
        VGroup(title[2], title[-1]).set_color(YELLOW)
        title.to_corner(UP+LEFT)

        neg_twelfth, eq, zeta_neg_1, sum_naturals = equation = OldTex(
            "-\\frac{1}{12}",
            "=",
            "\\zeta(-1)",
            "= 1 + 2 + 3 + 4 + \\cdots"
        )
        neg_twelfth.set_color(GREEN_B)
        VGroup(*zeta_neg_1[2:4]).set_color(YELLOW)
        q_mark = OldTex("?").next_to(sum_naturals[0], UP)
        q_mark.set_color(RED)
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)
        analytic_continuation = OldTexText("Analytic continuation")
        analytic_continuation.next_to(title, RIGHT, 3*LARGE_BUFF)

        sum_to_zeta = Arrow(title.get_corner(DOWN+RIGHT), zeta_neg_1)
        sum_to_ac = Arrow(title.get_right(), analytic_continuation)
        ac_to_zeta = Arrow(analytic_continuation.get_bottom(), zeta_neg_1.get_top())
        cross = OldTex("\\times")
        cross.scale(2)
        cross.set_color(RED)
        cross.rotate(np.pi/6)
        cross.move_to(sum_to_zeta.get_center())

        brace = Brace(VGroup(zeta_neg_1, sum_naturals))
        words = OldTexText(
            "If not equal, at least connected",
            "\\\\(see links in description)"
        )
        words.next_to(brace, DOWN)

        self.add(neg_twelfth, eq, zeta_neg_1, randy, title)
        self.wait()
        self.play(
            Write(sum_naturals),
            Write(q_mark),
            randy.change_mode, "confused"
        )
        self.play(Blink(randy))
        self.wait()
        self.play(randy.change_mode, "angry")
        self.play(
            ShowCreation(sum_to_zeta),
            Write(cross)
        )
        self.play(Blink(randy))
        self.wait()
        self.play(
            Transform(sum_to_zeta, sum_to_ac),
            FadeOut(cross),
            Write(analytic_continuation),
            randy.change_mode, "pondering",
            randy.look_at, analytic_continuation,
        )
        self.play(ShowCreation(ac_to_zeta))
        self.play(Blink(randy))
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(words[0]),
            randy.look_at, words[0],
        )
        self.wait()
        self.play(FadeIn(words[1]))
        self.play(Blink(randy))
        self.wait()

class InventingMathPreview(Scene):
    def construct(self):
        rect = Rectangle(height = 9, width = 16)
        rect.set_height(4)
        title = OldTexText("What does it feel like to invent math?")
        title.next_to(rect, UP)
        sum_tex = OldTex("1+2+4+8+\\cdots = -1")
        sum_tex.set_width(rect.get_width()-1)

        self.play(
            ShowCreation(rect),
            Write(title)
        )
        self.play(Write(sum_tex))
        self.wait()

class FinalAnimationTease(Scene):
    def construct(self):
        morty = Mortimer().shift(2*(DOWN+RIGHT))
        bubble = morty.get_bubble(SpeechBubble)
        bubble.write("""
            Want to know what
            $\\zeta'(s)$ looks like?
        """)

        self.add(morty)
        self.play(
            morty.change_mode, "hooray",
            morty.look_at, bubble.content,
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(morty))
        self.wait()

class PatreonThanks(Scene):
    CONFIG = {
        "specific_patrons" : [
            "CrypticSwarm",
            "Ali Yahya",
            "Damion Kistler",
            "Juan Batiz-Benet",
            "Yu Jun",
            "Othman Alikhan",
            "Markus Persson",
            "Joseph John Cox",
            "Luc Ritchie",
            "Shimin Kuang",
            "Einar Johansen",
            "Rish Kundalia",
            "Achille Brighton",
            "Kirk Werklund",
            "Ripta Pasay",
            "Felipe Diniz",
        ]
    }
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)

        n_patrons = len(self.specific_patrons)
        special_thanks = OldTexText("Special thanks to:")
        special_thanks.set_color(YELLOW)
        special_thanks.shift(3*UP)
        patreon_logo = ImageMobject("patreon", invert = False)
        patreon_logo.set_height(1.5)
        patreon_logo.next_to(special_thanks, DOWN)

        left_patrons = VGroup(*list(map(TexText,
            self.specific_patrons[:n_patrons/2]
        )))
        right_patrons = VGroup(*list(map(TexText,
            self.specific_patrons[n_patrons/2:]
        )))
        for patrons, vect in (left_patrons, LEFT), (right_patrons, RIGHT):
            patrons.arrange(DOWN, aligned_edge = LEFT)
            patrons.next_to(special_thanks, DOWN)
            patrons.to_edge(vect, buff = LARGE_BUFF)

        self.add(patreon_logo)
        self.play(morty.change_mode, "gracious")
        self.play(Write(special_thanks, run_time = 1))
        self.play(
            Write(left_patrons),
            morty.look_at, left_patrons
        )
        self.play(
            Write(right_patrons),
            morty.look_at, right_patrons
        )
        self.play(Blink(morty))
        for patrons in left_patrons, right_patrons:
            for index in 0, -1:
                self.play(morty.look_at, patrons[index])
                self.wait()

class CreditTwo(Scene):
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)
        morty.to_edge(RIGHT)

        brother = PiCreature(color = GOLD_E)
        brother.next_to(morty, LEFT)
        brother.look_at(morty.eyes)

        headphones = Headphones(height = 1)
        headphones.move_to(morty.eyes, aligned_edge = DOWN)
        headphones.shift(0.1*DOWN)

        url = OldTexText("www.audible.com/3blue1brown")
        url.to_corner(UP+RIGHT, buff = LARGE_BUFF)

        self.add(morty)
        self.play(Blink(morty))
        self.play(
            FadeIn(headphones),
            Write(url),
            Animation(morty)
        )
        self.play(morty.change_mode, "happy")
        for x in range(4):
            self.wait()
            self.play(Blink(morty))
        self.wait()
        self.play(
            FadeIn(brother),
            morty.look_at, brother.eyes
        )
        self.play(brother.change_mode, "surprised")
        self.play(Blink(brother))
        self.wait()
        self.play(
            morty.look, LEFT,
            brother.change_mode, "happy",
            brother.look, LEFT
        )
        for x in range(10):
            self.play(Blink(morty))
            self.wait()
            self.play(Blink(brother))
            self.wait()

class FinalAnimation(ZetaTransformationScene):
    CONFIG = {
        "min_added_anchors" : 100,
    }
    def construct(self):
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.add_reflected_plane()
        title = OldTex("s", "\\to \\frac{d\\zeta}{ds}(", "s", ")")
        title.set_color_by_tex("s", YELLOW)
        title.add_background_rectangle()
        title.scale(1.5)
        title.to_corner(UP+LEFT)

        self.play(Write(title))
        self.add_foreground_mobjects(title)
        self.wait()
        self.apply_complex_function(d_zeta, run_time = 8)
        self.wait()

class Thumbnail(ZetaTransformationScene):
    CONFIG = {
        "anchor_density" : 35
    }
    def construct(self):
        self.y_min = -4
        self.y_max = 4
        self.x_min = 1
        self.x_max = int(FRAME_X_RADIUS+2)
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.add_reflected_plane()
        # self.apply_zeta_function()
        self.plane.set_stroke(width = 4)

        div_sum = OldTex("-\\frac{1}{12} = ", "1+2+3+4+\\cdots")
        div_sum.set_width(FRAME_WIDTH-1)
        div_sum.to_edge(DOWN)
        div_sum.set_color(YELLOW)
        div_sum.set_background_stroke(width=8)
        # for mob in div_sum.submobjects:
        #     mob.add_to_back(BackgroundRectangle(mob))

        zeta = OldTex("\\zeta(s)")
        zeta.set_height(FRAME_Y_RADIUS-1)
        zeta.to_corner(UP+LEFT)

        million = OldTex("\\$1{,}000{,}000")
        million.set_width(FRAME_X_RADIUS+1)
        million.to_edge(UP+RIGHT)
        million.set_color(GREEN_B)
        million.set_background_stroke(width=8)

        self.add(div_sum, million, zeta)

class ZetaThumbnail(Scene):
    def construct(self):
        plane = ComplexPlane(
            x_range=(-5, 5), y_range=(-3, 3),
            background_line_style={
                "stroke_width": 2,
                "stroke_opacity": 0.75,
            }
        )
        plane.set_height(FRAME_HEIGHT)
        plane.scale(3 / 2.5)
        plane.add_coordinate_labels(font_size=12)
        # self.add(plane)

        lines = VGroup(
            *(
                Line(plane.c2p(-7, y), plane.c2p(7, y))
                for y in np.arange(-2, 2, 0.1)
                if y != 0
            ),
            *(
                Line(plane.c2p(x, -4), plane.c2p(x, 4))
                for x in np.arange(-2, 2, 0.1)
                if x != 0
            ),
        )
        lines.insert_n_curves(200)
        lines.apply_function(lambda p: plane.n2p(zeta(plane.p2n(p))))
        lines.make_smooth()
        lines.set_stroke(GREY_B, 1, opacity=0.5)
        # self.add(lines)

        c_line = Line(plane.c2p(0.5, 0), plane.c2p(0.5, 35))
        c_line.insert_n_curves(1000)
        c_line.apply_function(lambda p: plane.n2p(zeta(plane.p2n(p))))
        c_line.make_smooth()
        c_line.set_stroke([TEAL, YELLOW], width=[7, 3])

        shadow = VGroup()
        for w in np.linspace(25, 0, 50):
            cc = c_line.copy()
            cc.set_stroke(BLACK, width=w, opacity=0.025)
            shadow.add(cc)

        self.add(shadow)
        self.add(c_line)

        sym = OldTex("\\zeta\\left(s\\right)")
        sym.set_height(1.5)
        sym.move_to(FRAME_WIDTH * LEFT / 4 + FRAME_HEIGHT * UP / 4)
        shadow = VGroup()
        for w in np.linspace(50, 0, 50):
            sc = sym.copy()
            sc.set_fill(opacity=0)
            sc.set_stroke(BLACK, width=w, opacity=0.05)
            shadow.add(sc)
        # self.add(shadow)
        # self.add(sym)

class ZetaPartialSums(ZetaTransformationScene):
    CONFIG = {
        "anchor_density" : 35,
        "num_partial_sums" : 12,
    }
    def construct(self):
        self.add_transformable_plane()
        self.add_extra_plane_lines_for_zeta()
        self.prepare_for_transformation(self.plane)

        N_list = [2**k for k in range(self.num_partial_sums)]
        sigma = OldTex(
            "\\sum_{n = 1}^N \\frac{1}{n^s}"
        )
        sigmas = []
        for N in N_list + ["\\infty"]:
            tex = OldTex(str(N))
            tex.set_color(YELLOW)
            new_sigma = sigma.copy()
            top = new_sigma[0]
            tex.move_to(top, DOWN)
            new_sigma.remove(top)
            new_sigma.add(tex)
            new_sigma.to_corner(UP+LEFT)
            sigmas.append(new_sigma)

        def get_partial_sum_func(n_terms):
            return lambda s : sum([1./(n**s) for n in range(1, n_terms+1)])
        interim_planes = [
            self.plane.copy().apply_complex_function(
                get_partial_sum_func(N)
            )
            for N in N_list
        ]
        interim_planes.append(self.plane.copy().apply_complex_function(zeta))
        symbol = VGroup(OldTex("s"))
        symbol.scale(2)
        symbol.set_color(YELLOW)
        symbol.to_corner(UP+LEFT)
        for plane, sigma in zip(interim_planes, sigmas):
            self.play(
                Transform(self.plane, plane),
                Transform(symbol, sigma)
            )
            self.wait()

