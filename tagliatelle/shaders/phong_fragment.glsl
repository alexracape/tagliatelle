#version 330
//#extension GL_OES_standard_derivatives : enable

struct LightInfo {
    vec3 world_position;
    vec4 color;
    vec3 ambient;
    int type;
    vec4 info;
    vec3 direction;
};

in vec3 world_position;
in vec3 normal;
in vec4 color;

uniform int num_lights;
uniform LightInfo lights[8];
uniform vec4 material_color;
uniform vec3 camera_position;

out vec4 f_color;

void main() {

    f_color = vec4(0.0, 0.0, 0.0, 1.0);
    int i = 0;
    while (i < num_lights){
        
        LightInfo light = lights[i];
        float intensity = light.info[0];
        float range = light.info[1];

        vec3 lightVector = light.world_position - world_position;
        float lightDistance = length(lightVector);
        
        vec3 L = normalize(lightVector);
        vec3 V = normalize(camera_position - world_position);
        vec3 N = normalize(normal);
        
        float falloff = 0.0;
        // Point Light
        if (light.type == 0)
            falloff = 1 / (1 + lightDistance * lightDistance);
            //falloff = 5;

        // Spot Light
        else if (light.type == 1) {
            falloff = 1 / (1.0 + lightDistance * lightDistance);
            float outer_angle = light.info[2];
            float inner_angle = light.info[3];
            float lightAngleScale = 1.0 / max(.001, cos(inner_angle) - cos(outer_angle));
            float lightAngleOffset = -cos(outer_angle) * lightAngleScale;
            float cd = dot(light.direction, L);
            float angularAttenuation = clamp((cd * lightAngleScale + lightAngleOffset), 0.0, 1.0);
            angularAttenuation *= angularAttenuation;
            falloff *= angularAttenuation;
        }

        // Directional Light
        else
            falloff = 1.0;
        
        // Computer diffuse
        vec4 diffuse = light.color * max(0.0, dot(L, N)) * falloff; // using lambertian attenuation

        // Compute Specular
        float shininess = 15.0;
        float specularStrength = 0.5;
        vec3 reflection = -reflect(L, N);
        float specularPower = pow(max(0.0, dot(V, reflection)), shininess);
        float specular = specularStrength * specularPower * falloff;

        // Get Ambient
        vec3 ambient = light.ambient;
        
        // Get diffuse color
        vec4 ccc = material_color;
        vec4 diffuseColor = color;
        f_color += diffuseColor * (diffuse + vec4(ambient, 1.0)) + specular;
        i += 1;
    } 
}