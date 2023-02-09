# Import javascript modules
from js import THREE, window, document, Object, console
# Import pyscript / pyodide modules
from pyodide.ffi import create_proxy, to_js
# Import python module
import math

# ----------------------------------------------------------------------------------------------------------
global tree_params    
tree_params = {  
        "size" : 2,
        "old_size" : 1,
        "height" :3,
        "old_height" : 1,
        "x" : 2,
        "y" : 4,
        "old_x" : 2,
        "old_y" : 1,
}
tree_params = Object.fromEntries(to_js(tree_params))


#-----------------------------------------------------------------------
#main
def main():
    #-----------------------------------------------------------------------
    # VISUAL SETUP
    # Declare the variables
    global renderer, scene, camera, controls,composer, texture

    #Set up the renderer
    renderer = THREE.WebGLRenderer.new()
    renderer.setPixelRatio( window.devicePixelRatio )
    renderer.setSize(window.innerWidth, window.innerHeight)

    document.body.appendChild(renderer.domElement)
    
    # texture = THREE.TextureLoader.new().load("green2.jpg")
    
    # Set up the scene
    scene = THREE.Scene.new()
    back_color = THREE.Color.new("rgb(255,255,255)")
    scene.background = back_color
    
    camera = THREE.PerspectiveCamera.new(40, window.innerWidth/window.innerHeight, 0.1, 10000)
    camera.position.z = 500
    camera.position.x = 500
    camera.position.y = 200

    scene.add(camera)

    
    # Graphic Post Processing
    global composer
    post_process()


    # Set up responsive window
    resize_proxy = create_proxy(on_window_resize)
    window.addEventListener('resize', resize_proxy) 
     #-----------------------------------------------------------------------

    # Mouse orbit
    controls = THREE.OrbitControls.new(camera, renderer.domElement)
    
   
    #GUI
    gui = window.lil.GUI.new()
    sizechanger = gui.addFolder('properties')
    sizechanger.add(tree_params, 'size')
    sizechanger.add(tree_params, 'height')
   
    sizechanger.open()

    param_folder = gui.addFolder('field')
    param_folder.add(tree_params, 'x', 2,20,1)
    param_folder.add(tree_params, 'y', 2,20,1)

    param_folder.open()
    #-----------------------------------------------------------------------
    # Geometry
    
    my_axiom_system = system(0, tree_params.size, "X")
    console.log(my_axiom_system)
    
    global color  
    color = THREE.Color.new('rgb(120,100,80)')
        
    draw_system(my_axiom_system, THREE.Vector3.new(0,0,0),color,15,math.pi/3, math.pi/3)

    
    
    #-----------------------------------------------------------------------
    # render update, 
    render()

# ----------------------------------------------------------------------------------------------------------

def update_landscape():
    if tree_params.old_x != tree_params.x or tree_params.old_y != tree_params.y or tree_params.old_size != tree_params.size or tree_params.old_height != tree_params.height:
        scene.clear()
                     
        for i in range(tree_params.x):
            for j in range(tree_params.y):
            
                my_axiom_system = system(0,tree_params.size, "X")
                
                draw_system(my_axiom_system, THREE.Vector3.new(i * 40,0,j*40),color,tree_params.height,math.pi/(3+(10/((i*0.5)*(j*0.5)+0.5))),math.pi/(3+(5/((j*0.5)*(i*0.5)+0.5))))
       
        tree_params.old_height = tree_params.height
        tree_params.old_size = tree_params.size
        tree_params.old_x = tree_params.x
        tree_params.old_y = tree_params.y
                 
        
 
        
          
#-----------------------------------------------------------------------
# rule 
def generate(symbol):

    if symbol == "X":
        return "[FX[+X][-X][*X][/X]X]"
    elif symbol == "F":
        return "FF"
    elif symbol == "+":
        return "+"
    elif symbol == "-":
        return "-"
    elif symbol == "[":
        return "["
    elif symbol == "]":
        return "]"
    elif symbol == "/":
        return "/"
    elif symbol == "*":
        return "*"
    
   
# ----------------------------------------------------------------------------------------------------------
# recursive function
def system(current_iteration, max_iterations, axiom):
    current_iteration += 1
    new_axiom = ""
    for symbol in axiom:
        new_axiom += generate(symbol)
    
    # print(current_iteration)
    # print(new_axiom)
 

    if current_iteration >= max_iterations:
        return new_axiom
    else:
        
        return system(current_iteration, max_iterations, new_axiom)


# ----------------------------------------------------------------------------------------------------------

def draw_system(axiom, start_pt,color,height, angle_z, angle_x):
    move_vec = THREE.Vector3.new(0,height,0)
    old_states = []
    old_move_vecs = []
    lines = []
    apples = []
    
    for symbol in axiom:
        if symbol == "F" or symbol == "X":
            old = THREE.Vector3.new(start_pt.x, start_pt.y, start_pt.z)
            new_pt = THREE.Vector3.new(start_pt.x, start_pt.y, start_pt.z)
            new_pt = new_pt.add(move_vec)
            
            line = []
            line.append(old)
            line.append(new_pt)
            lines.append(line)

            start_pt = new_pt
            
            if old.x != new_pt.x or old.z != new_pt.z:
                apples.append(new_pt)
        
        
             
        elif symbol == "+": 
            move_vec.applyAxisAngle(THREE.Vector3.new(0,0,1), angle_z)
        
        elif symbol == "-": 
            move_vec.applyAxisAngle(THREE.Vector3.new(0,0,1), -angle_z)
            
        elif symbol == "/": 
            move_vec.applyAxisAngle(THREE.Vector3.new(1,0,0), angle_x)
        
        elif symbol == "*":
            move_vec.applyAxisAngle(THREE.Vector3.new(1,0,0), -angle_x)
        
        elif symbol == "[":
            old_state = THREE.Vector3.new(start_pt.x, start_pt.y, start_pt.z)
            old_move_vec = THREE.Vector3.new(move_vec.x, move_vec.y, move_vec.z)
            old_states.append(old_state)
            old_move_vecs.append(old_move_vec)              

        elif symbol == "]":
            start_pt = THREE.Vector3.new(old_states[-1].x, old_states[-1].y, old_states[-1].z)
            move_vec = THREE.Vector3.new(old_move_vecs[-1].x, old_move_vecs[-1].y, old_move_vecs[-1].z)
            old_states.pop(-1)
            old_move_vecs.pop(-1)
            
      
    
    for points in lines:
        
        line_geom = THREE.BufferGeometry.new()
        points = to_js(points)
        
        console.log(points)

        line_geom.setFromPoints( points )
        

        line_material = THREE.LineBasicMaterial.new(color)
        line_material.color = color
        
        vis_line = THREE.Line.new(line_geom, line_material)
        
        scene.add(vis_line)
        
        
    for points in apples:
        # print(points.x)
        
        apple = THREE.SphereGeometry.new(0.5,15, 15)
        apple.translate(points.x, points.y - 0.5, points.z)
    
        points = to_js(points)
        console.log(points)
    
        
        color_apple = THREE.Color.new(255, 0, 0)
        material = THREE.MeshBasicMaterial.new(color_apple)
        material.transparent = True
        material.opacity = 0.2
        material.color = color  
        material.color = color_apple
        
        spheres = THREE.Mesh.new(apple, material)
        
        scene.add(spheres)
                
        
    
# ----------------------------------------------------------------------------------------------------------

# Simple render and animate
def render(*args):
    window.requestAnimationFrame(create_proxy(render))
    update_landscape()

    controls.update()
    composer.render()
    
    

# Graphical post-processing
def post_process():
    render_pass = THREE.RenderPass.new(scene, camera)
    render_pass.clearColor = THREE.Color.new(0,0,0)
    render_pass.ClearAlpha = 0
    fxaa_pass = THREE.ShaderPass.new(THREE.FXAAShader)

    pixelRatio = window.devicePixelRatio

    fxaa_pass.material.uniforms.resolution.value.x = 1 / ( window.innerWidth * pixelRatio )
    fxaa_pass.material.uniforms.resolution.value.y = 1 / ( window.innerHeight * pixelRatio )
   
    global composer
    composer = THREE.EffectComposer.new(renderer)
    composer.addPass(render_pass)
    composer.addPass(fxaa_pass)

# window size
def on_window_resize(event):

    event.preventDefault()

    global renderer
    global camera
    
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()

    renderer.setSize( window.innerWidth, window.innerHeight )

    #post processing after resize
    post_process()
#-----------------------------------------------------------------------
#RUN THE MAIN PROGRAM
if __name__=='__main__':
    main()
