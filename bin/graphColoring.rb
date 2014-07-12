require "libz3"
require "./bin/polygon.rb"

class Edge

    def initialize(startPoint, endPoint)
        @start = startPoint
        @end = endPoint
    end

end

class Vertice

    attr_accessor :x, :y

    def initialize(x,y)
        @x = x
        @y = y
    end

    def ==(otherVertice)
        return @x == otherVertice.x && @y == otherVertice.y
    end

end

class Polygon
    @@colors = [:blue, :white, :green, :yellow]

    attr_accessor :color, :edges, :vertices
 
    def initialize(*vertices)
        @color = 0
        always { @color.in @@colors }
        
        @vertices = vertices.map { |rawVertice| Vertice.new(rawVertice[0], rawVertice[1]) }

        @edges = []
        self.construct_edges
    end

    def construct_edges
        for i in 0..@vertices.size-1 
            @edges.push(Edge.new(@vertices[i], @vertices[i+1]))
        end
        @edges.push(Edge.new(@vertices.last, @vertices.first))
    end

    def move_by(x,y)
        @vertices.each do |v|
            v.x += x
            v.y += y
        end 
    end

    def has_common_vertices?(anotherPolygon)
        return anotherPolygon.vertices.any? { |v| @vertices.any? { |v2| v == v2 } }
    end

end

# Polygons
ll = Polygon.new [0,0], [5,0], [5,5], [0,5]
ul = Polygon.new [0,0], [5,0], [5,5], [0,5]
ul.move_by(0,5)

lm = Polygon.new [0,0], [5,0], [5,5], [0,5]
lm.move_by(5,0)
um = Polygon.new [0,0], [5,0], [5,5], [0,5]
um.move_by(5,5)

lr = Polygon.new [0,0], [5,0], [5,5], [0,5]
lr.move_by(10,0)
ur = Polygon.new [0,0], [5,0], [5,5], [0,5]
ur.move_by(10,5)

polygons = [ul, um, ur, ll, lm, lr]
polygons.each do |onePolygon|
    polygons.each do |anotherPolygon|
        if(onePolygon != anotherPolygon && onePolygon.has_common_vertices?(anotherPolygon) )
            always { onePolygon.color != anotherPolygon.color }
        end
    end
end

polygons.each do |p|
    puts p.color
end
