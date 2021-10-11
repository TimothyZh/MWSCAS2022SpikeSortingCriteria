


%raw_data=block8.segments{1, 1}.analogsignals{1, 2}.signal;
raw_data=transpose(data)
%plot(raw_data)
fs = 24000;
%f_data=raw_data
f_data = bandpass(raw_data, [300 3000], fs);
a=abs(f_data);
a=a/0.6745;

thr=4*(median(a,'all'));
%f_data = f_data(1:2000000); 
%plot (f_data) 

counter=0;
spike = double.empty; 
s=[]; 

spiket=[]

counter=0;
spike = double.empty; 
spikeAligned=double.empty;
s=[]; 
sAligned=[];

spiket=[]
spiketMax=[]
spiketcounter=0
%peak alignment spikes
for i= 1:length(f_data)
    if counter==0
        
        if f_data(i)>((1)*thr) %| f_data(i)<((-1)*thr)
            counter=1
            spiketcounter=spiketcounter+1
            spiket=[spiket;i]
            for j=1:5
                s(end+1)=f_data(i-6+j)
            end
        end
    end
    
    if counter>28
        [maxv,maxind]=max(s)
        sAligned=f_data(spiket(spiketcounter)-5-(16-maxind):spiket(spiketcounter)+26-(16-maxind))
        spikeAligned=[spikeAligned,sAligned];
        spiketMax=[spiketMax;spiket(spiketcounter)+maxind]
        spike=[spike;s];
        
        plot(s)
        hold on
        counter=0
        s=double.empty
        sAligned=double.empty

    end
    
    if counter>0 && counter<29
        s(end+1)=f_data(i)
        counter=counter+1
    end
    

            
end


%yline(thr)






        