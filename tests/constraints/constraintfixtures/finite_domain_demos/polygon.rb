    class Polygon
        @@colors = [:blue, :green, :yellow, :red]

        attr_reader :color

        def initialize()
            always { @color.in @@colors }
        end

        def addNeighbour(neighbour)
            @neighbours ||= []
            @neighbours.push(neighbour)
        end

        def neighbourOf?(potentialNeighbour)
            @neighbours ||= []
            return @neighbours.include? potentialNeighbour
        end

    end

    def createMap()

        smallGreenMiddle = Polygon.new()
        smallBlueMiddle = Polygon.new()
        largeRedLeft = Polygon.new()
        spikeyBlueLeft = Polygon.new()
        spikeyGreenRight = Polygon.new()
        tinyRedRight = Polygon.new()
        largeRedRight = Polygon.new()
        middleBlueRight = Polygon.new()
        tinyYellowRight = Polygon.new()
        tinyBlueRight = Polygon.new()
        bigBlueLowerLeft = Polygon.new()
        ballGreenLowerLeft = Polygon.new()
        outerYellowLowerLeft = Polygon.new()
        ballYellowLeft = Polygon.new()
        roundYellowUpperRight = Polygon.new()
        roundYellowUpperLeft = Polygon.new()
        ballBlueLowerLeft = Polygon.new()
        largeGreenLowerRight = Polygon.new()
        blueFormTop = Polygon.new()
        spikeyBlueRight = Polygon.new()
        crownGreenMiddle = Polygon.new()
        eggBlueMiddle = Polygon.new()
        lowerEggBlueMiddle = Polygon.new()
        ballRedBottom = Polygon.new()
        outerBallRedBottom = Polygon.new()
        outerBallBlueBottom = Polygon.new()
        hexagonYellowLeft = Polygon.new()
        rectangleRedMiddle = Polygon.new()
        starYellowLowerRight = Polygon.new()
        crossGreenTop = Polygon.new()

        smallGreenMiddle.addNeighbour(rectangleRedMiddle)
        smallGreenMiddle.addNeighbour(spikeyBlueLeft)
        smallGreenMiddle.addNeighbour(smallBlueMiddle)
        smallGreenMiddle.addNeighbour(lowerEggBlueMiddle)
        smallGreenMiddle.addNeighbour(largeRedLeft)

        smallBlueMiddle.addNeighbour(hexagonYellowLeft)
        smallBlueMiddle.addNeighbour(smallGreenMiddle)
        smallBlueMiddle.addNeighbour(largeRedLeft)
        smallBlueMiddle.addNeighbour(rectangleRedMiddle)
        smallBlueMiddle.addNeighbour(outerBallRedBottom)

        largeRedLeft.addNeighbour(roundYellowUpperLeft)
        largeRedLeft.addNeighbour(crossGreenTop)
        largeRedLeft.addNeighbour(eggBlueMiddle)
        largeRedLeft.addNeighbour(spikeyBlueLeft)
        largeRedLeft.addNeighbour(hexagonYellowLeft)
        largeRedLeft.addNeighbour(outerBallBlueBottom)

        spikeyBlueLeft.addNeighbour(largeRedLeft)
        spikeyBlueLeft.addNeighbour(smallGreenMiddle)
        spikeyBlueLeft.addNeighbour(crownGreenMiddle)

        spikeyGreenRight.addNeighbour(spikeyBlueRight)
        spikeyGreenRight.addNeighbour(tinyYellowRight)
        spikeyGreenRight.addNeighbour(largeRedRight)
        spikeyGreenRight.addNeighbour(tinyBlueRight)
        spikeyGreenRight.addNeighbour(tinyRedRight)
        spikeyGreenRight.addNeighbour(middleBlueRight)
        spikeyGreenRight.addNeighbour(rectangleRedMiddle)
        spikeyGreenRight.addNeighbour(lowerEggBlueMiddle)

        tinyRedRight.addNeighbour(middleBlueRight)
        tinyRedRight.addNeighbour(spikeyGreenRight)

        largeRedRight.addNeighbour(roundYellowUpperRight)
        largeRedRight.addNeighbour(tinyBlueRight)
        largeRedRight.addNeighbour(tinyYellowRight)
        largeRedRight.addNeighbour(spikeyBlueRight)
        largeRedRight.addNeighbour(eggBlueMiddle)

        middleBlueRight.addNeighbour(spikeyGreenRight)
        middleBlueRight.addNeighbour(tinyRedRight)
        middleBlueRight.addNeighbour(largeGreenLowerRight)
        middleBlueRight.addNeighbour(starYellowLowerRight)
        middleBlueRight.addNeighbour(rectangleRedMiddle)

        tinyYellowRight.addNeighbour(spikeyGreenRight)
        tinyYellowRight.addNeighbour(largeRedRight)
        #tinyYellowRight.addNeighbour(spikeyBlueRight)

        tinyBlueRight.addNeighbour(largeRedRight)
        tinyBlueRight.addNeighbour(spikeyGreenRight)
        tinyBlueRight.addNeighbour(tinyRedRight)

        bigBlueLowerLeft.addNeighbour(rectangleRedMiddle)
        bigBlueLowerLeft.addNeighbour(largeGreenLowerRight)
        bigBlueLowerLeft.addNeighbour(ballRedBottom)
        bigBlueLowerLeft.addNeighbour(outerBallRedBottom)

        ballGreenLowerLeft.addNeighbour(ballRedBottom)
        ballGreenLowerLeft.addNeighbour(outerYellowLowerLeft)
        ballGreenLowerLeft.addNeighbour(ballYellowLeft)

        outerYellowLowerLeft.addNeighbour(ballGreenLowerLeft)
        outerYellowLowerLeft.addNeighbour(outerBallBlueBottom)
        outerYellowLowerLeft.addNeighbour(bigBlueLowerLeft)

        ballYellowLeft.addNeighbour(outerBallBlueBottom)
        ballYellowLeft.addNeighbour(ballBlueLowerLeft)
        ballYellowLeft.addNeighbour(ballGreenLowerLeft)

        roundYellowUpperRight.addNeighbour(blueFormTop)
        roundYellowUpperRight.addNeighbour(crossGreenTop)
        roundYellowUpperRight.addNeighbour(largeRedRight)

        roundYellowUpperLeft.addNeighbour(crossGreenTop)
        roundYellowUpperLeft.addNeighbour(largeRedLeft)
        roundYellowUpperLeft.addNeighbour(blueFormTop)

        ballBlueLowerLeft.addNeighbour(ballYellowLeft)
        ballBlueLowerLeft.addNeighbour(ballRedBottom)
        ballBlueLowerLeft.addNeighbour(outerBallRedBottom)

        largeGreenLowerRight.addNeighbour(middleBlueRight)
        largeGreenLowerRight.addNeighbour(starYellowLowerRight)
        largeGreenLowerRight.addNeighbour(rectangleRedMiddle)
        largeGreenLowerRight.addNeighbour(bigBlueLowerLeft)

        blueFormTop.addNeighbour(roundYellowUpperRight)
        blueFormTop.addNeighbour(roundYellowUpperLeft)
        blueFormTop.addNeighbour(crossGreenTop)

        spikeyBlueRight.addNeighbour(largeRedRight)
        spikeyBlueRight.addNeighbour(spikeyGreenRight)
        spikeyBlueRight.addNeighbour(crownGreenMiddle)
        #spikeyBlueRight.addNeighbour(tinyYellowRight)

        crownGreenMiddle.addNeighbour(spikeyBlueRight)
        crownGreenMiddle.addNeighbour(eggBlueMiddle)
        crownGreenMiddle.addNeighbour(lowerEggBlueMiddle)
        crownGreenMiddle.addNeighbour(spikeyBlueLeft)

        eggBlueMiddle.addNeighbour(crownGreenMiddle)
        eggBlueMiddle.addNeighbour(largeRedRight)
        eggBlueMiddle.addNeighbour(crossGreenTop)
        eggBlueMiddle.addNeighbour(largeRedLeft)

        eggBlueMiddle.addNeighbour(crownGreenMiddle)
        eggBlueMiddle.addNeighbour(spikeyGreenRight)
        eggBlueMiddle.addNeighbour(rectangleRedMiddle)
        eggBlueMiddle.addNeighbour(smallGreenMiddle)

        ballRedBottom.addNeighbour(ballBlueLowerLeft)
        ballRedBottom.addNeighbour(bigBlueLowerLeft)
        ballRedBottom.addNeighbour(ballGreenLowerLeft)

        outerBallRedBottom.addNeighbour(bigBlueLowerLeft)
        outerBallRedBottom.addNeighbour(ballBlueLowerLeft)
        outerBallRedBottom.addNeighbour(outerBallBlueBottom)
        outerBallRedBottom.addNeighbour(hexagonYellowLeft)
        outerBallRedBottom.addNeighbour(smallBlueMiddle)

        outerBallBlueBottom.addNeighbour(outerBallRedBottom)
        outerBallBlueBottom.addNeighbour(largeRedLeft)
        outerBallBlueBottom.addNeighbour(hexagonYellowLeft)
        outerBallBlueBottom.addNeighbour(ballYellowLeft)
        outerBallBlueBottom.addNeighbour(outerYellowLowerLeft)

        hexagonYellowLeft.addNeighbour(largeRedLeft)
        hexagonYellowLeft.addNeighbour(smallBlueMiddle)
        hexagonYellowLeft.addNeighbour(outerBallRedBottom)
        hexagonYellowLeft.addNeighbour(outerBallBlueBottom)

        rectangleRedMiddle.addNeighbour(smallBlueMiddle)
        rectangleRedMiddle.addNeighbour(smallGreenMiddle)
        rectangleRedMiddle.addNeighbour(lowerEggBlueMiddle)
        rectangleRedMiddle.addNeighbour(spikeyGreenRight)
        rectangleRedMiddle.addNeighbour(middleBlueRight)
        rectangleRedMiddle.addNeighbour(starYellowLowerRight)
        rectangleRedMiddle.addNeighbour(largeGreenLowerRight)
        rectangleRedMiddle.addNeighbour(bigBlueLowerLeft)


        return [smallGreenMiddle ,
        smallBlueMiddle ,
        largeRedLeft ,
        spikeyBlueLeft ,
        spikeyGreenRight ,
        tinyRedRight ,
        largeRedRight ,
        middleBlueRight ,
        tinyYellowRight ,
        tinyBlueRight ,
        bigBlueLowerLeft ,
        ballGreenLowerLeft ,
        outerYellowLowerLeft ,
        ballYellowLeft ,
        roundYellowUpperRight ,
        roundYellowUpperLeft ,
        ballBlueLowerLeft ,
        largeGreenLowerRight ,
        blueFormTop ,
        spikeyBlueRight ,
        crownGreenMiddle ,
        eggBlueMiddle ,
        lowerEggBlueMiddle ,
        ballRedBottom ,
        outerBallRedBottom ,
        outerBallBlueBottom ,
        hexagonYellowLeft ,
        rectangleRedMiddle ,
        starYellowLowerRight ,
        crossGreenTop]

    end

    def render(elements)
        return @completeMap % elements.map { |e| @colorCodes[e.color] }
    end

    @colorCodes = { :green => "#328925", :red => "#e2001a", 
                    :yellow => "ffec00", :blue => "#009ee0" }


    @completeMap = %Q{
<svg
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:xlink="http://www.w3.org/1999/xlink"
   version="1.0"
   width="300"
   height="400"
   viewBox="0 0 521.361 472.969"
   id="Layer_1"
   xml:space="preserve"><metadata/><defs
   id="defs2528"><clipPath
     id="XMLID_4_">
		<use
   id="use2442"
   x="0"
   y="0"
   width="521.36102"
   height="472.96899"
   xlink:href="#XMLID_1_" />
	</clipPath></defs>


<g
   transform="matrix(1.73787,0,0,1.73787,-210.28227,-130.08963)"
   id="g2436">
	<defs
   id="defs2438">
		<rect
   width="280"
   height="380"
   x="131"
   y="20.933001"
   id="XMLID_1_" />
	</defs>
	<clipPath
   id="clipPath2539">
		<use
   id="use2541"
   x="0"
   y="0"
   width="521.36102"
   height="472.96899"
   xlink:href="#XMLID_1_" />
	</clipPath>
	<g
   clip-path="url(#XMLID_4_)"
   id="XMLID_2_">
		<g
   id="g2445">
			<path
   d="M 220.9,203.763 C 223.08,201.943 225.3,200.183 227.58,198.483 C 231.57,209.493 237.28,219.683 244.38,228.733 L 219.62,240.933 L 220.9,203.763 z "
   style="fill:%s"
   id="path2447" />
			<path
   d="M 244.38,228.732 C 246.61,231.583 248.98,234.322 251.48,236.932 C 246.82,242.912 241.68,248.502 236.13,253.652 C 222.25,246.092 206.47,241.572 189.69,241.003 C 197.87,226.843 208.46,214.242 220.9,203.763 L 219.62,240.933 L 244.38,228.732 z "
   style="fill:%s"
   id="path2449" />
			<path
   d="M 221.61,149.323 L 177.29,142.083 L 213.1,175.303 L 153.8,196.943 L 221,200.933 L 220.9,203.763 C 208.46,214.242 197.87,226.843 189.69,241.003 C 188.47,240.952 187.24,240.933 186,240.933 C 165.83,240.933 146.99,246.613 131,256.473 L 131,39.712 L 250.46,86.032 C 234.65,103.002 224.16,124.982 221.61,149.323 z "
   style="fill:%s"
   id="path2451" />
			<path
   d="M 227.58,198.482 C 225.3,200.182 223.08,201.942 220.9,203.762 L 221,200.932 L 153.8,196.942 L 213.1,175.302 L 177.29,142.082 L 221.61,149.322 C 221.21,153.142 221,157.012 221,160.932 C 221,174.123 223.32,186.763 227.58,198.482 z "
   style="fill:%s"
   id="path2453" />
			<path
   d="M 386.54,193.033 C 390.48,195.563 394.28,198.293 397.94,201.193 L 319.95,202.723 L 325.179,240.933 L 272.4,214.933 L 263.08,219.523 C 270.8,205.813 276.269,190.673 279,174.603 C 289.28,172.203 299.99,170.933 311,170.933 C 318.94,170.933 326.73,171.593 334.32,172.873 L 331.7,175.303 L 386.519,193.023 C 386.53,193.033 386.53,193.033 386.54,193.033 z "
   style="fill:%s"
   id="path2455" />
			<path
   d="M 411,200.933 L 411,212.943 C 406.9,208.763 402.53,204.833 397.94,201.193 L 411,200.933 z "
   style="fill:%s"
   id="path2457" />
			<path
   d="M 278.85,126.383 C 276.79,114.703 273.27,103.513 268.5,93.023 L 411,148.283 L 411,200.933 L 386.54,193.033 C 386.53,193.033 386.53,193.033 386.519,193.023 C 370.95,183.033 353.28,176.043 334.32,172.873 L 367.509,142.083 L 298.789,153.303 L 278.85,126.383 z "
   style="fill:%s"
   id="path2459" />
			<path
   d="M 325.18,240.933 L 319.951,202.723 L 397.941,201.193 C 402.531,204.833 406.901,208.763 411.001,212.943 L 411.001,236.414 C 390.961,257.664 362.531,270.934 331.001,270.934 C 299.731,270.934 271.511,257.884 251.481,236.934 C 255.761,231.444 259.641,225.624 263.081,219.524 L 272.401,214.934 L 325.18,240.933 z "
   style="fill:%s"
   id="path2461" />
			<path
   d="M 331.7,175.303 L 334.32,172.873 C 353.28,176.043 370.95,183.033 386.519,193.023 L 331.7,175.303 z "
   style="fill:%s"
   id="path2463" />
			<path
   d="M 411,200.933 L 397.94,201.193 C 394.28,198.293 390.48,195.563 386.54,193.033 L 411,200.933 z "
   style="fill:%s"
   id="path2465" />
			<path
   d="M 291,345.933 C 291,366.103 285.32,384.943 275.46,400.933 L 203.75,400.933 C 191.38,386.203 181.99,368.903 176.5,349.933 C 179.56,350.583 182.74,350.933 186,350.933 C 210.85,350.933 231,330.783 231,305.933 C 231,291.573 224.27,278.783 213.79,270.543 C 221.8,265.663 229.28,259.992 236.13,253.652 C 268.82,271.442 291,306.093 291,345.933 z "
   style="fill:%s"
   id="path2467" />
			<path
   d="M 173,287.263 C 171.68,294.963 171,302.863 171,310.933 C 171,324.463 172.92,337.553 176.5,349.933 C 156.21,345.563 141,327.523 141,305.933 C 141,300.663 141.91,295.603 143.58,290.903 C 153.68,290.723 163.53,289.473 173,287.263 z "
   style="fill:%s"
   id="path2469" />
			<path
   d="M 203.75,400.933 L 131,400.933 L 131,290.583 C 134.3,290.812 137.64,290.933 141,290.933 C 141.86,290.933 142.72,290.923 143.58,290.903 C 141.91,295.603 141,300.664 141,305.933 C 141,327.523 156.21,345.563 176.5,349.933 C 181.99,368.902 191.38,386.202 203.75,400.933 z "
   style="fill:%s"
   id="path2471" />
			<path
   d="M 180.04,261.322 C 176.9,269.623 174.52,278.293 173,287.262 C 163.53,289.472 153.68,290.722 143.58,290.902 C 149.12,275.242 163.09,263.572 180.04,261.322 z "
   style="fill:%s"
   id="path2473" />
			<path
   d="M 411,85.453 L 411,148.283 L 268.5,93.023 C 265.98,87.473 263.1,82.123 259.91,76.993 C 279.08,60.733 303.889,50.933 331,50.933 C 362.53,50.933 390.96,64.203 411,85.453 z "
   style="fill:%s"
   id="path2475" />
			<path
   d="M 259.91,76.993 C 256.58,79.813 253.41,82.833 250.46,86.033 L 131,39.712 L 131,20.932 L 193.06,20.932 C 220.85,32.073 244.25,51.873 259.91,76.993 z "
   style="fill:%s"
   id="path2477" />
			<path
   d="M 186,260.933 C 196.48,260.933 206.14,264.523 213.79,270.543 C 201.34,278.143 187.61,283.843 173,287.263 C 174.52,278.293 176.9,269.623 180.04,261.323 C 181.99,261.063 183.98,260.933 186,260.933 z "
   style="fill:%s"
   id="path2479" />
			<path
   d="M 411,236.413 L 411,400.933 L 275.46,400.933 C 285.32,384.943 291,366.103 291,345.933 C 291,306.093 268.82,271.443 236.13,253.653 C 241.68,248.504 246.82,242.914 251.48,236.933 C 271.51,257.883 299.73,270.933 331,270.933 C 362.53,270.933 390.96,257.663 411,236.413 z "
   style="fill:%s"
   id="path2481" />
			<path
   d="M 411,20.933 L 411,85.453 C 390.96,64.203 362.53,50.933 331,50.933 C 303.89,50.933 279.08,60.733 259.91,76.993 C 244.25,51.873 220.85,32.073 193.06,20.933 L 411,20.933 L 411,20.933 z "
   style="fill:%s"
   id="path2483" />
			<path
   d="M 367.51,142.083 L 334.321,172.873 C 326.731,171.593 318.941,170.933 311.001,170.933 C 299.991,170.933 289.281,172.203 279.001,174.603 C 280.321,166.903 281.001,159.003 281.001,150.933 C 281.001,142.553 280.261,134.353 278.851,126.383 L 298.791,153.303 L 367.51,142.083 z "
   style="fill:%s"
   id="path2485" />
			<path
   d="M 278.85,126.383 C 280.26,134.353 281,142.553 281,150.933 C 281,159.003 280.32,166.903 279,174.603 C 260.1,179.023 242.67,187.273 227.58,198.483 C 223.32,186.763 221,174.123 221,160.933 C 221,157.013 221.21,153.143 221.61,149.323 L 246.01,153.303 L 272.401,117.673 L 278.85,126.383 z "
   style="fill:%s"
   id="path2487" />
			<path
   d="M 278.85,126.383 L 272.401,117.673 L 246.01,153.303 L 221.61,149.323 C 224.16,124.983 234.65,103.003 250.46,86.033 L 268.5,93.023 C 273.27,103.513 276.79,114.703 278.85,126.383 z "
   style="fill:%s"
   id="path2489" />
			<path
   d="M 279,174.603 C 276.27,190.673 270.8,205.813 263.08,219.523 L 244.38,228.733 C 237.28,219.683 231.57,209.493 227.58,198.483 C 242.67,187.272 260.1,179.022 279,174.603 z "
   style="fill:%s"
   id="path2491" />
			<path
   d="M 213.79,270.543 C 224.27,278.782 231,291.572 231,305.933 C 231,330.783 210.85,350.933 186,350.933 C 182.74,350.933 179.56,350.583 176.5,349.933 C 172.92,337.553 171,324.463 171,310.933 C 171,302.863 171.68,294.963 173,287.263 C 187.61,283.843 201.34,278.143 213.79,270.543 z "
   style="fill:%s"
   id="path2493" />
			<path
   d="M 236.13,253.652 C 229.28,259.992 221.8,265.663 213.79,270.543 C 206.14,264.522 196.48,260.933 186,260.933 C 183.98,260.933 181.99,261.063 180.04,261.323 C 182.72,254.263 185.95,247.473 189.69,241.004 C 206.47,241.572 222.25,246.093 236.13,253.652 z "
   style="fill:%s"
   id="path2495" />
			<path
   d="M 186,240.933 C 187.24,240.933 188.47,240.953 189.69,241.003 C 185.95,247.473 182.72,254.263 180.04,261.322 C 163.09,263.572 149.12,275.242 143.58,290.902 C 142.72,290.923 141.86,290.932 141,290.932 C 137.64,290.932 134.3,290.812 131,290.582 L 131,256.472 C 146.99,246.612 165.83,240.933 186,240.933 z "
   style="fill:%s"
   id="path2497" />
		</g>
		<g
   id="g2499">
			<polygon
   points="411,236.413 411,400.933 275.46,400.933 203.75,400.933 131,400.933 131,290.583 131,256.473 131,39.712 131,20.933 193.06,20.933 411,20.933 411,85.453 411,148.283 411,200.933 411,212.942 411,236.413 "
   style="fill:none;stroke:#000000;stroke-width:2"
   id="polygon2501" />
			<path
   d="M 278.85,126.383 C 280.26,134.353 281,142.553 281,150.933 C 281,159.003 280.32,166.903 279,174.603 C 276.27,190.673 270.8,205.813 263.08,219.523 C 259.64,225.624 255.76,231.443 251.48,236.933 C 246.82,242.913 241.68,248.503 236.13,253.653 C 229.28,259.993 221.8,265.664 213.79,270.544 C 201.34,278.144 187.61,283.844 173,287.264 C 163.53,289.474 153.68,290.724 143.58,290.904 C 142.72,290.925 141.86,290.934 141,290.934 C 137.64,290.934 134.3,290.814 131,290.584 C 120.46,289.834 110.25,287.934 100.49,284.983 C 42.92,267.603 1,214.163 1,150.933 C 1,93.193 35.96,43.613 85.86,22.203 C 102.78,14.953 121.42,10.933 141,10.933 C 159.4,10.933 176.97,14.483 193.06,20.933 C 220.85,32.073 244.25,51.873 259.91,76.993 C 263.1,82.123 265.98,87.473 268.5,93.023 C 273.27,103.513 276.79,114.703 278.85,126.383 z "
   style="fill:none;stroke:#000000;stroke-width:2"
   id="path2503" />
			<path
   d="M 221.61,149.323 C 221.21,153.143 221,157.013 221,160.933 C 221,174.123 223.32,186.763 227.58,198.483 C 231.57,209.493 237.28,219.683 244.38,228.733 C 246.61,231.584 248.98,234.323 251.48,236.933 C 271.51,257.883 299.73,270.933 331,270.933 C 362.53,270.933 390.96,257.663 411,236.413 C 414.61,232.612 417.93,228.553 420.95,224.263 C 433.58,206.363 441,184.513 441,160.933 C 441,160.593 441,160.243 440.99,159.903 C 440.73,131.083 429.389,104.913 411,85.453 C 390.96,64.203 362.53,50.933 331,50.933 C 303.89,50.933 279.08,60.733 259.91,76.993 C 256.58,79.813 253.41,82.833 250.46,86.033 C 234.65,103.002 224.16,124.982 221.61,149.323 z "
   style="fill:none;stroke:#000000;stroke-width:2"
   id="path2505" />
			<path
   d="M 386.52,193.022 C 370.951,183.032 353.281,176.042 334.321,172.872 C 326.731,171.592 318.941,170.932 311.001,170.932 C 299.991,170.932 289.281,172.202 279.001,174.602 C 260.101,179.022 242.671,187.272 227.581,198.482 C 225.301,200.182 223.081,201.942 220.901,203.762 C 208.461,214.241 197.871,226.842 189.691,241.002 C 185.951,247.472 182.721,254.262 180.041,261.321 C 176.901,269.622 174.521,278.292 173.001,287.261 C 171.681,294.961 171.001,302.861 171.001,310.931 C 171.001,324.461 172.921,337.551 176.501,349.931 C 181.991,368.901 191.381,386.201 203.751,400.931 C 214.871,414.161 228.391,425.311 243.651,433.691 C 263.631,444.681 286.591,450.931 311.001,450.931 C 388.321,450.931 451.001,388.251 451.001,310.931 C 451.001,278.201 439.771,248.101 420.951,224.261 C 417.841,220.311 414.52,216.531 411.001,212.941 C 406.901,208.761 402.531,204.831 397.941,201.191 C 394.281,198.291 390.481,195.561 386.541,193.031"
   style="fill:none;stroke:#000000;stroke-width:2"
   id="path2507" />
			<path
   d="M 275.46,400.933 C 285.32,384.943 291,366.103 291,345.933 C 291,306.093 268.82,271.443 236.13,253.653 C 222.25,246.093 206.47,241.573 189.69,241.004 C 188.47,240.953 187.24,240.934 186,240.934 C 165.83,240.934 146.99,246.614 131,256.474 C 119.02,263.854 108.64,273.564 100.49,284.984 C 88.22,302.173 81,323.202 81,345.933 C 81,403.923 128.01,450.933 186,450.933 C 207.3,450.933 227.11,444.593 243.65,433.693 C 256.5,425.242 267.38,414.043 275.46,400.933 z "
   style="fill:none;stroke:#000000;stroke-width:2"
   id="path2509" />
			<path
   d="M 176.5,349.933 C 156.21,345.563 141,327.523 141,305.933 C 141,300.663 141.91,295.603 143.58,290.903 C 149.12,275.243 163.09,263.573 180.04,261.323 C 181.99,261.063 183.98,260.933 186,260.933 C 196.48,260.933 206.14,264.523 213.79,270.543 C 224.27,278.782 231,291.572 231,305.933 C 231,330.783 210.85,350.933 186,350.933 C 182.74,350.933 179.56,350.583 176.5,349.933 z "
   style="fill:none;stroke:#000000;stroke-width:2"
   id="path2511" />
			<path
   d="M 221.61,149.323 L 246.01,153.303 L 272.401,117.673 L 278.85,126.383 L 298.79,153.303 L 367.51,142.083 L 334.321,172.873 L 331.701,175.303 L 386.52,193.023 C 386.531,193.033 386.531,193.033 386.541,193.033 L 411.001,200.933 L 397.941,201.193 L 319.951,202.723 L 325.18,240.933 L 272.401,214.933 L 263.081,219.523 L 244.381,228.733 L 219.621,240.933 L 220.901,203.763 L 221.001,200.933 L 153.801,196.943 L 213.101,175.303 L 177.291,142.083 L 221.61,149.323 z "
   style="fill:none;stroke:#000000;stroke-width:2"
   id="path2513" />
			<polyline
   points="31,0.933 85.86,22.203 131,39.712 250.46,86.033 268.5,93.022      411,148.283 440.99,159.903 521,190.933    "
   id="polyline2515"
   style="fill:none;stroke:#000000;stroke-width:2" />
		</g>
	</g>
	<polygon
   points="201,250.185 178.68,248.845 168.68,228.845 181,210.185 203.32,211.524 213.32,231.524 201,250.185 "
   style="fill:%s;stroke:#000000;stroke-width:2"
   clip-path="url(#XMLID_4_)"
   id="polygon2517" />
	<path
   d="M 351,308.185 C 351,314.812 345.627,320.185 339,320.185 L 253,320.185 C 246.373,320.185 241,314.812 241,308.185 L 241,212.185 C 241,205.558 246.373,200.185 253,200.185 L 339,200.185 C 345.627,200.185 351,205.558 351,212.185 L 351,308.185 z "
   style="fill:%s;stroke:#000000;stroke-width:2"
   clip-path="url(#XMLID_4_)"
   id="path2519" />
	<polygon
   points="352.564,260.185 396.803,319.811 471,317.172 427.963,377.67 453.401,447.421 382.564,425.185 324.089,470.933 323.347,396.691 261.768,355.214 332.146,331.566 352.564,260.185 "
   style="fill:%s;stroke:#000000;stroke-width:2"
   clip-path="url(#XMLID_4_)"
   id="polygon2521" />
	<polygon
   points="251,30.933 271,30.933 271,60.933 331,60.933 331,80.933 271,80.933 271,110.933 251,110.933 251,80.933 201,80.933 201,60.933 251,60.933 251,30.933 "
   style="fill:%s;stroke:#000000;stroke-width:2"
   clip-path="url(#XMLID_4_)"
   id="polygon2523" />
</g>

<rect
   width="486.60361"
   height="660.39063"
   x="17.378696"
   y="-93.710815"
   style="fill:none;stroke:#000000;stroke-width:5.21361017;stroke-linecap:round"
   id="rect2525" /></svg>
    }
