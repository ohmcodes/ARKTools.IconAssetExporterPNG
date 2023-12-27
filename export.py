import unreal
import os
import json

project_path = "/Game/"
base_directory = 'path_to your_directory'

def exportPNG(asset):
  savePath = base_directory + str(asset.package_name) + '.png'
  asset_object = unreal.EditorAssetLibrary.load_asset(asset.package_name)

  pngExporter = unreal.TextureExporterPNG()
  
  exportTask = unreal.AssetExportTask()
  exportTask.automated = True
  exportTask.exporter = pngExporter
  exportTask.filename = savePath
  
  exportTask.object = asset_object
  exportTask.prompt = False
  exportTask.replace_identical = True
  
  check = unreal.Exporter.run_asset_export_task(exportTask)

  if check==True:
    print(f"Exported {str(asset.package_name)} to {str(asset.package_path)}")
    pass
  else:
    print(f"PNG export error {str(asset.package_name)}")
    return

def createObject(results, asset):
  current_dict = results
  path_components = str(asset.package_path).replace("/Game/","").split('/')
  for component in path_components:
    current_dict = current_dict.setdefault(component, {})

  current_dict[str(asset.asset_name)] = str(asset.package_name) + "." + str(asset.asset_name)
   
  return results

def generate_markdown(result, depth=0, lastKey=''):
    markdown = ''
    for key, value in result.items():
      if isinstance(value, str):
          directory_path = os.path.dirname(value) + '/' + key + '.png'

          markdown += f'<div style="background-color:rgba(255, 255, 255, 0.3); vertical-align: middle;"><img height="20" alt="" src="{directory_path}"> '
          markdown += f'{key} </div>\n\n'
          markdown += f'```\n{value}\n```\n\n'
      else:
          markdown += '<details>\n'
          markdown += f'<summary>{key}</summary>\n'
          markdown += generate_markdown(value, depth + 1, key)
          markdown += '\n</details>\n'
          markdown += f'\n--- End of {lastKey}/{key} ---\n' 

    return markdown

def LoopUEAssets():
  asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
  all_assets = asset_registry.get_assets_by_path(project_path, recursive=True)
  counter = 0
  results = {}

  # Filter unnecessary folders IconGenerator and UltraDynamicSky
  for asset in all_assets:
    if ("Icons" in str(asset.package_name) or "Icon" in str(asset.package_path)) and "IconGenerator" not in str(asset.package_path) and "UltraDynamicSky" not in str(asset.package_path) and asset.asset_class_path.asset_name=='Texture2D':
      # Export PNG
      exportPNG(asset)
      # Create object for each directory
      results = createObject(results, asset)
      counter = counter+1

  print(counter)
  
  # Convert the nested dictionary to JSON with double quotes
  json_string = json.dumps(results, ensure_ascii=False, indent=2)
  # Write JSON data to a file
  with open(base_directory+'icons.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_string)

  markdown = generate_markdown(results)
  # Write Markdown content to a file
  with open(base_directory+'icons.md', 'w', encoding='utf-8') as markdown_file:
    markdown_file.write(markdown)
        
# Call Entry point
LoopUEAssets()
