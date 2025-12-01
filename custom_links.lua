local path = require("pandoc.path")

local github_repo = "https://github.com/zonca/zonca.dev"
local raw_repo = "https://raw.githubusercontent.com/zonca/zonca.dev/main/"

local function current_input_path()
  local input_file = quarto.doc and quarto.doc.input_file or nil
  if not input_file or input_file == "" then
    return nil
  end

  local normalized = path.normalize(input_file)
  local cwd = pandoc.system.get_working_directory()
  local project_dir = (quarto.project and quarto.project.directory) or cwd
  local relative = path.make_relative(normalized, project_dir)

  if not relative or relative == "" then
    return nil
  end

  return relative
end

local function is_post(relative_path)
  if not relative_path then
    return false
  end
  -- Check if the file is in the posts/ directory
  return string.match(relative_path, "^posts/") ~= nil
end

local function build_buttons_html()
  local relative_path = current_input_path()
  if not relative_path or not is_post(relative_path) then
    return nil
  end

  local edit_url = github_repo .. "/edit/main/" .. relative_path
  local download_url = raw_repo .. relative_path

  local download_button = string.format(
    '<a href="%s" class="btn btn-outline-secondary" role="button" target="_blank" rel="noopener">Download source</a>',
    download_url
  )
  local contribute_button = string.format(
    '<a href="%s" class="btn btn-primary" role="button" target="_blank" rel="noopener">Contribute</a>',
    edit_url
  )

  return string.format(
    '<div class="page-action-buttons d-flex flex-wrap gap-2">%s%s</div>',
    download_button,
    contribute_button
  )
end

local function build_buttons_block()
  local buttons = build_buttons_html()
  if not buttons then
    return nil
  end

  return pandoc.RawBlock('html',
    '<div class="page-action-container mb-4">' .. buttons .. '</div>')
end

local M = {}

-- relref shortcode: converts a filename to a relative URL
-- Usage: {{< relref "filename.md" >}} or {{< relref "posts/filename.md" >}}
M['relref'] = function(args, kwargs, meta)
  if #args < 1 then
    return pandoc.Null()
  end
  
  local target = pandoc.utils.stringify(args[1])
  -- Remove any leading/trailing quotes
  target = target:gsub('^"', ''):gsub('"$', '')
  
  -- Remove .md extension and replace with .html for the URL
  local url_path = target:gsub("%.md$", ".html"):gsub("%.qmd$", ".html")
  
  -- Handle both "filename.md" and "posts/filename.md" formats
  if not url_path:match("^posts/") then
    -- If it doesn't start with posts/, add it
    url_path = "posts/" .. url_path
  end
  
  -- Build absolute URL for the site
  local url = "/" .. url_path
  
  return pandoc.Str(url)
end

M['custom_links'] = function(args, kwargs, meta)
  local buttons = build_buttons_html()
  if not buttons then
    return pandoc.Null()
  end

  return pandoc.RawBlock('html', buttons)
end

M['Pandoc'] = function(doc)
  if quarto.doc.is_format("html") then
    local block = build_buttons_block()
    if block then
      table.insert(doc.blocks, 1, block)
    end
  end

  return doc
end

return M
