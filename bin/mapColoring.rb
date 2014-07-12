require "libz3"
require "./bin/polygon.rb"

class Polygon
    @@colors = [:blue, :green, :yellow, :red]

    attr_reader :color

    def initialize()
        always { @color.in @@colors }
    end

end


polygons = createMap()
polygons.each do |onePolygon|
    polygons.each do |anotherPolygon|
        if(onePolygon != anotherPolygon && onePolygon.neighbourOf?(anotherPolygon) )
            always { onePolygon.color != anotherPolygon.color }
        end
    end
end

svg = render(polygons)

f = File.open("./resultMap.svg", "w")
f.write(svg)
f.close()

