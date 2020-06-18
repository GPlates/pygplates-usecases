#GMT Plot a line chart

#plot areas of different features: ELand, TLand, OCean, and entire Earth

gmt psxy A_ELand.txt -JX-15/8 -R0/400/0.5/3.5 -Ba50f10:"Time (Ma)":/a0.5f0.5:"Area  x10^14 sqm":SW -P -W1,red -K > psfile_3.ps
gmt psxy A_ELand.txt -J -R -Sc0.2 -Gred -P -O -K >> psfile_3.ps

gmt psxy A_TLand.txt -J -R -P -W1,blue -O -K >> psfile_3.ps
gmt psxy A_TLand.txt -J -R -Sc0.2 -Gblue -P -O -K >> psfile_3.ps

gmt psxy A_Ocean.txt -J -R -P -W1,purple -O -K >> psfile_3.ps
gmt psxy A_Ocean.txt -J -R -Sc0.2 -Gpurple -P -O >> psfile_3.ps

#gmt psxy A_Earth.txt -JX12/5 -R -P -W1,green -O >> psfile_2.ps

gmt ps2raster psfile_3.ps -Tg -A