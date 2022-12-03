# Import javascript modules
from js import THREE, window, document, Object
# Import pyscript / pyodide modules
from pyodide.ffi import create_proxy, to_js
# Import python module
import math

# ----------------------------------------------------------------------------------------------------------

def main():
    #-----------------------------------------------------------------------

    global renderer, scene, camera, controls,composer, axesHelper
    
    #renderer
    renderer = THREE.WebGLRenderer.new()
    renderer.setPixelRatio( window.devicePixelRatio )
    renderer.setSize(window.innerWidth, window.innerHeight)
    document.body.appendChild(renderer.domElement)

    #scene
    scene = THREE.Scene.new()
    back_color = THREE.Color.new(1,1,1)
    scene.background = back_color
    camera = THREE.PerspectiveCamera.new(75, window.innerWidth/window.innerHeight, 0.1, 1000)
    camera.position.z = 50
    scene.add(camera)

    # Graphic Post Processing
    global composer
    post_process()

    #axesHelper
    axesHelper = THREE.AxesHelper.new(100)
    scene.add(axesHelper)
    
    #responsive window
    resize_proxy = create_proxy(on_window_resize)
    window.addEventListener('resize', resize_proxy) 
   
    #-----------------------------------------------------------------------
    # Geometry 
    global geom1_params, cubes, cube_lines
    
    cubes = []
    cube_lines = []
    
    
    geom1_params = {
        "size" : 2,
        "scale": 0.5,
        "x" : 3, 
        "y" : 5,
        "z" : 4,
        "rotation":0,
        "rotation2":0,

    }
    
    geom1_params = Object.fromEntries(to_js(geom1_params))
    
    
    #create Materials
    global material, line_material
    
    color = THREE.Color.new(255, 0, 0)
    material = THREE.MeshBasicMaterial.new(color)
    material.transparent = True
    material.opacity = 0.5
    material.color = color
    
    line_material = THREE.LineBasicMaterial.new()
    line_material.color = THREE.Color.new(255,0,0)
    
    Matrix()
    
    
    #-----------------------------------------------------------------------
    # Mouse orbit control
    controls = THREE.OrbitControls.new(camera, renderer.domElement)

    # GUI
    gui = window.dat.GUI.new()
    param_folder = gui.addFolder('Parameters')
    param_folder.add(geom1_params, 'size', 0.5,10,0.1)
    param_folder.add(geom1_params, 'scale', 0.5,1,0.1)
    param_folder.add(geom1_params, 'x', 1,15,1)
    param_folder.add(geom1_params, 'y', 1,30,1)
    param_folder.add(geom1_params, 'z', 1,20,1)
    param_folder.add(geom1_params, 'rotation', 0,180)
    param_folder.add(geom1_params, 'rotation2', 0,180)
  
    param_folder.open()
    
    #-----------------------------------------------------------------------
    render()
    
# ----------------------------------------------------------------------------------------------------------


                    
def Matrix():
        for k in range(geom1_params.y):
            for i in range(geom1_params.x):
                for j in range(geom1_params.z):
                
                    #for update
                    global z,sizeold, scaleold, rotateold
                    z = geom1_params.rotation2
                    sizeold = geom1_params.size
                    scaleold = geom1_params.scale
                    rotateold = geom1_params.rotation
                    
                    #generate geometry
                    geom = THREE.BoxGeometry.new(geom1_params.size*geom1_params.scale*(i+1), geom1_params.size, geom1_params.size*geom1_params.scale*(j+1))
                    
                    geom.translate((geom1_params.size*i)*(geom1_params.size+i), geom1_params.size*k, (geom1_params.size*j)*(geom1_params.size+j))
                    
                    cube = THREE.Mesh.new(geom, material)
                    
                    #rotating around center
                    bbox = THREE.Box3.new()
                    bbox.setFromObject(cube)
                    center = THREE.Vector3.new()
                    bbox.getCenter(center)
                    center.normalize()
                    cube.rotateOnAxis(center, math.radians(geom1_params.rotation))
    
                    #rotating around axis
                    geom.rotateY(math.radians(geom1_params.rotation2)/geom1_params.y*k)
                
                     
                    cubes.append(cube)
                    
                    #generate line
                    edges = THREE.EdgesGeometry.new(cube.geometry)
                    line = THREE.LineSegments.new(edges, line_material)
                    line.rotateOnAxis(center, math.radians(geom1_params.rotation))
                    
                    cube_lines.append(line)
                    scene.add(line,cube)
                
                

# ----------------------------------------------------------------------------------------------------------
               
def update_cubes():
    global cubes, cube_lines, material, line_material
    # Make sure you dont have zero cubes 
    
    if len(cubes) != 0 :
        if len(cubes) != geom1_params.x * geom1_params.y * geom1_params.z:
            for cube in cubes: scene.remove(cube)
            for cube in cube_lines: scene.remove(cube)
            
            cube = []
            cube_lines = []
            
            Matrix()
    
        
    if z != geom1_params.rotation2 or sizeold != geom1_params.size or scaleold != geom1_params.scale or rotateold != geom1_params.rotation:
        for cube in cubes: scene.remove(cube)
        for cube in cube_lines: scene.remove(cube)
            
        cube = []
        cube_lines = []
           
        Matrix()
    
 
        
        
            
        
            


                

# ----------------------------------------------------------------------------------------------------------
               
# Simple render and animate
def render(*args):
    window.requestAnimationFrame(create_proxy(render))
    update_cubes()
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

# Adjust display when window size changes
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
