import Graphics.Rendering.Chart.Easy
import Graphics.Rendering.Chart.Backend.Cairo

toBin 0 = [ 0 ] 
toBin n = toBin (n `quot` 2) ++ [n `rem` 2]

radinv x = foldl (+) 0 (map (\(a,b)->a*b) $ zip (map fromIntegral $ toBin x) (map (2^^) [(negate $ length $ toBin x) .. 0]))

thePoints :: Int -> [(Rational,Rational)]
thePoints n = map (\(a,b)-> (toRational a, toRational b)) $ [((realToFrac i)/(realToFrac n),radinv i) | i <- [0 .. n-1]]

toFloat x = fromRational x :: Float

main = do
    a <- getLine
    b <- return $ map (\(x,y) -> (toFloat $ x, toFloat $ y)) $ thePoints (read a :: Int)
    toFile def ("hammersleys" ++ a ++ ".png") $ do
        layout_title .= "Hammersley points"
        layout_background .= solidFillStyle (opaque white)
        layout_foreground .= (opaque black)
        plot (points "Points" b)
