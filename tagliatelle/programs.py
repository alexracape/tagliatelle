import os

import numpy as np
from moderngl_window.scene import MeshProgram

current_dir = os.path.dirname(__file__)


class BaseProgram(MeshProgram):
    """
    Default Program
    """

    def __init__(self, ctx, **kwargs):
        super().__init__(program=None)
        
        # Vertex Shader
        vertex_path = os.path.join(current_dir, "shaders/base_vertex.glsl")
        vertex = open(vertex_path, 'r').read()

        # Fragment Shader
        fragment_path = os.path.join(current_dir, "shaders/base_fragment.glsl")
        fragment = open(fragment_path, 'r').read()
    
        self.program = ctx.program(vertex_shader=vertex, fragment_shader=fragment)

    def draw(
        self,
        mesh,
        projection_matrix=None,
        model_matrix=None,
        camera_matrix=None,
        time=0,
    ):

        self.program["m_proj"].write(projection_matrix)
        self.program["m_model"].write(model_matrix)
        self.program["m_cam"].write(camera_matrix)

        if mesh.material:
            self.program["material_color"].value = tuple(mesh.material.color)
        else:
            self.program["material_color"].value = (1.0, 1.0, 1.0, 1.0)

        mesh.vao.render(self.program)
    
    def apply(self, mesh):
        return self


class PhongProgram(MeshProgram):
    """
    Instance Rendering Program with Phong Shading
    """
    current_camera_matrix = None
    camera_position = None

    def __init__(self, ctx, num_instances, **kwargs):
        super().__init__(program=None)
        self.num_instances = num_instances

        # Vertex Shader
        vertex_path = os.path.join(current_dir, "shaders/phong_vertex.glsl")
        vertex = open(vertex_path, 'r').read()

        # Fragment Shader
        fragment_path = os.path.join(current_dir, "shaders/phong_fragment.glsl")
        fragment = open(fragment_path, 'r').read()

        self.program = ctx.program(vertex_shader=vertex, fragment_shader=fragment)

    def draw(
        self,
        mesh,
        projection_matrix=None,
        model_matrix=None,
        camera_matrix=None,
        time=0,
    ):

        self.program["m_proj"].write(projection_matrix)
        self.program["m_model"].write(model_matrix)
        self.program["m_cam"].write(camera_matrix)

        # Only invert matrix / calculate camera position if camera is moved
        if list(camera_matrix) != PhongProgram.current_camera_matrix:
            PhongProgram.current_camera_matrix = list(camera_matrix)
            camera_world = np.linalg.inv(camera_matrix).m4
            PhongProgram.camera_position = tuple(camera_world[:3])
        self.program["camera_position"].value = PhongProgram.camera_position
        #print(f"Camera Position: {PhongProgram.camera_position}")

        if mesh.material:
            self.program["material_color"].value = tuple(mesh.material.color)
        else:
            self.program["material_color"].value = (1.0, 1.0, 1.0, 1.0)

        lights = mesh.lights.values()
        num_lights = len(lights)
        self.program["num_lights"].value = num_lights

        # Set light values - better way to pass dict directly?
        for i, light in zip(range(num_lights), lights):
            for attr, val in light.items():
                self.program[f"lights[{i}].{attr}"].value = val
       
        positions = [light.get("world_position") for light in lights]
        print(f"Light Positions: {positions}")
        mesh.vao.render(self.program, instances = self.num_instances)
    
    def apply(self, mesh):
        return self
