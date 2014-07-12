require "libz3"
require "./demo/polygon.rb"

class Symbol
  def constraint_solver
    Z3::Instance
  end
end

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
    svg = render(polygons)
    f = File.open("./demo/resultMap.svg", "w")
    f.write(svg)
    f.close()
    sleep(1)
    puts "Round"
    end
