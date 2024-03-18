require 'net/http'
require 'uri'

def send_log(label, content)
  url = URI.parse("http://localhost/logger/index.php?label=#{URI.encode(label)}&t=#{URI.encode(content)}")
  response = Net::HTTP.get_response(url)

  if response.is_a?(Net::HTTPSuccess)
    return response.body
  else
    return "Error: #{response.message}"
  end
end

# Example usage:
label = "Example Label"
content = "This is the log content"
result = send_log(label, content)
puts result
