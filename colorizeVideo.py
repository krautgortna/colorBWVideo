import imageio, os, shutil, json
import Algorithmia
from Algorithmia.acl import ReadAcl, AclType

reader = imageio.get_reader('../roadkill.mp4')
fps = reader.get_meta_data()['fps']

#writer = imageio.get_writer('roadkill_colorized.mp4', fps=fps)

out_dir = os.path.join(os.getcwd(), 'images')
out_dir_colorized = os.path.join(os.getcwd(), 'colorized_images')

# Authenticate with your API key
f = open("apikey", "r") 
apiKey = f.read().splitlines()[0]
# Create the Algorithmia client object
client = Algorithmia.client(apiKey)


# Instantiate a DataDirectory object, set your data URI and call create
roadkill_dir = client.dir("data://krautgortna/roadkill")
# Create your data collection if it does not exist
if roadkill_dir.exists() is False:
  roadkill_dir.create()
  
  # Create the acl object and check if it's the .my_algos default setting
  acl = roadkill_dir.get_permissions()  # Acl object
  acl.read_acl == AclType.my_algos  # True

  # Update permissions to private
  roadkill_dir.update_permissions(ReadAcl.private)
  roadkill_dir.get_permissions().read_acl == AclType.private # True



c = 1
for im in reader:
  if(c < 26):
    c = c+1
    continue
    
  print("Frame #" + str(c))
  filename = 'roadkill' + str(c) + '.png'
  output = os.path.join(out_dir, filename)
  print("...write image to local disk")
  imageio.imwrite(output, im[:, :, :])
  
  print("...upload image to algorithmia")
  remoteImage = "data://krautgortna/roadkill/" + filename
  if client.file(remoteImage).exists() is False:
    client.file(remoteImage).putFile(output)
    
    
  print("...call colorizing algo on algorithmia")
  input = {
    "image": remoteImage
  }
  algo = client.algo('deeplearning/ColorfulImageColorization/1.1.13')
  response = algo.pipe(input).result
  remote_result = response['output']
  print("...remote result = " + remote_result)
  
  # Download the file
  if client.file(remote_result).exists() is True:
    localfile = client.file(remote_result).getFile()
    print("...local file = " + localfile.name)
    
    result_filename = 'roadkill' + str(c) + '.png'
    colorized = os.path.join(out_dir_colorized, result_filename)
    #os.rename(localfile.name, colorized)
    shutil.move(localfile.name, colorized)
    
    #im_color = imageio.imread(colorized)
    #writer.append_data(im_color[:, :, 1])
  
  c = c + 1

#writer.close()



