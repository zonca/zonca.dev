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

local function build_buttons_html()
  local relative_path = current_input_path()
  if not relative_path then
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
