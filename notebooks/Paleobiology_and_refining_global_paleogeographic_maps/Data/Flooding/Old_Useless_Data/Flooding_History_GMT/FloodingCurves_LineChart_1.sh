# GMT Plot a line chart

#Plot the global flooding history curve

#gmt psxy Flooding_Rate_410_0Ma.txt -JX-15/10 -R0/400/0.3/0.6 -Ba50f10:"Time (Ma)":/a0.05f0.01:"Flooding Ratio":SW -P -W1,red -K > psfile_1.ps
#gmt psxy Flooding_Rate_410_0Ma.txt -J -R -Sc0.2 -Gred -P -O -K >> psfile_1.ps


gmt psxy sealevel_from_volume_20080130.txt -JX-12/16 -R0/140/45/175 -Ba10f5:"Time (Ma)":/a10f5:"Sea level (m)":SW -P -W1,red -K >> psfile_2.ps
gmt psxy sealevel_from_volume_20080130.txt -J -R -Sc0.2 -Gred -P -O >> psfile_2.ps

gmt ps2raster psfile_2.ps -Tg -A -P
