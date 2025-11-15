return {
  ['custom_links'] = function(args, kwargs, meta)
    -- Get the input file path
    local input_file = quarto.doc.input_file

    -- Construct the GitHub URLs
    local github_repo = "https://github.com/zonca/zonca.dev"
    local edit_url = github_repo .. "/edit/main/" .. input_file
    local download_url = "https://raw.githubusercontent.com/zonca/zonca.dev/main/" .. input_file

    -- Create the HTML for the links
    local contribute_button = '<a href="' .. edit_url .. '" class="btn btn-light" role="button" target="_blank">Contribute</a>'
    local download_link = '<a href="' .. download_url .. '" download style="display: none;">Download</a>'

    -- Return the HTML as a raw block
    return pandoc.RawBlock('html', download_link .. '\n' .. contribute_button)
  end
}
