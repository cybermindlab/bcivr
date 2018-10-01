import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import matplotlib.mlab as mlab

# Echo server program
import socket
import time


#Recuperado de EEGrunt
def remove_dc_offset(data,fs):
	hp_cutoff_Hz = 1.0
	b,a=signal.butter(2, hp_cutoff_Hz/(fs/ 2.0), 'highpass')
	data=signal.lfilter(b,a,data,0)
	return data

def bandpass(data,fs,fl,fh):
	bp_Hz=np.zeros(0)
	bp_Hz=np.array([fl,fh])
	b,a=signal.butter(3,bp_Hz/(fs/ 2.0),'bandpass')
	return signal.lfilter(b, a, data, 0)

def notch_mains_interference(data,fs):
	notch_freq_Hz = np.array([60.0])
	for freq_Hz in np.nditer(notch_freq_Hz):
		bp_stop_Hz = freq_Hz + 3.0*np.array([-1, 1])
		b, a = signal.butter(3, bp_stop_Hz/(fs/ 2.0), 'bandstop')
		data = signal.lfilter(b, a, data, 0)
	return data
	
def get_spectrum_data(data,fs,L,overlap):
	spec_PSDperHz,spec_freqs,spec_t=mlab.specgram(data,NFFT=L,Fs=fs,window=mlab.window_hanning,noverlap=overlap)
	spec_PSDperBin=spec_PSDperHz*fs/float(L)
	return spec_PSDperHz,spec_freqs,spec_t,spec_PSDperBin

#Nombre del archivo OpenBCI
file=open("openBCI_2013-12-24_meditation.txt",'r')

#Deteccion de filas que comienzan con %
filas=file.readline()
while filas:
	if filas[0]!="%":
		break
	filas=file.readline()

CH1=[]
CH2=[]

fs=250
L=256

overlap=L-int(0.25*fs)
print(overlap)


freq=np.fft.rfftfreq(L,1/fs)

eeg_bands={'Delta': (2, 4),
           'Theta': (4, 8),
           'Alpha': (8, 12),
           'Beta': (12, 30),
           'Gamma': (30, 45)}

relax=[];

i=0
while filas:
	#Extrayendo Ch1
	Ch1=filas.split(" ")[1]
	Ch1=float(Ch1.replace(",",""))
	CH1.append(Ch1)
	#Extrayendo Ch2
	Ch2=filas.split(" ")[2];
	Ch2=float(Ch2.replace(",",""))
	CH2.append(Ch2)
	
	filas=file.readline()

#Filtro se
CH1=remove_dc_offset(CH1,fs)
CH1=notch_mains_interference(CH1,fs)
CH1=bandpass(CH1,fs,3,50)
CH2=remove_dc_offset(CH2,fs)
CH2=notch_mains_interference(CH2,fs)
CH2=bandpass(CH2,fs,3,50)

spec_PSDperHz1,spec_freqs,spec_t,spec_PSDperBin1=get_spectrum_data(CH1,fs,L,overlap)
spec_PSDperHz2,spec_freqs,spec_t,spec_PSDperBin2=get_spectrum_data(CH1,fs,L,overlap)

N1=spec_PSDperHz1.shape[1]
N2=spec_PSDperHz2.shape[1]

freq_theta=[]
freq_alpha=[]
freq_beta=[]
for i in range(0,len(spec_freqs)):
	if ((spec_freqs[i]>=eeg_bands['Theta'][0]) & (spec_freqs[i]<=eeg_bands['Theta'][1])):
		freq_theta.append(1)
	else:
		freq_theta.append(0)
	if ((spec_freqs[i]>=eeg_bands['Alpha'][0]) & (spec_freqs[i]<=eeg_bands['Alpha'][1])):
		freq_alpha.append(1)
	else:
		freq_alpha.append(0)
	if ((spec_freqs[i]>=eeg_bands['Beta'][0]) & (spec_freqs[i]<=eeg_bands['Beta'][1])):
		freq_beta.append(1)
	else:
		freq_beta.append(0)




CH1power_theta=[]
CH1power_alpha=[]
CH1power_beta=[]
for i in range(0,N1):
	theta=np.multiply(freq_theta,spec_PSDperHz1[:,i])
	CH1power_theta.append(sum(np.multiply(theta,theta)))
	alpha=np.multiply(freq_alpha,spec_PSDperHz1[:,i])
	CH1power_alpha.append(sum(np.multiply(alpha,alpha)))
	beta=np.multiply(freq_beta,spec_PSDperHz1[:,i])
	CH1power_beta.append(sum(np.multiply(beta,beta)))

CH2power_theta=[]
CH2power_alpha=[]
CH2power_beta=[]
for i in range(0,N2):
	theta=np.multiply(freq_theta,spec_PSDperHz2[:,i])
	CH2power_theta.append(sum(np.multiply(theta,theta)))
	alpha=np.multiply(freq_alpha,spec_PSDperHz2[:,i])
	CH2power_alpha.append(sum(np.multiply(alpha,alpha)))
	beta=np.multiply(freq_beta,spec_PSDperHz2[:,i])
	CH2power_beta.append(sum(np.multiply(beta,beta)))	


CH1power_theta=np.array(CH1power_theta)
CH1power_alpha=np.array(CH1power_alpha)
CH1power_beta=np.array(CH1power_beta)
CH2power_theta=np.array(CH2power_theta)
CH2power_alpha=np.array(CH2power_alpha)
CH2power_beta=np.array(CH2power_beta)

power_theta=(CH1power_theta+CH2power_theta)/2/(eeg_bands['Theta'][1]-eeg_bands['Theta'][0])
power_alpha=(CH1power_alpha+CH2power_alpha)/2/(eeg_bands['Alpha'][1]-eeg_bands['Alpha'][0])
power_beta=(CH1power_beta+CH2power_beta)/2/(eeg_bands['Beta'][1]-eeg_bands['Beta'][0])


power_theta=(CH1power_theta+CH2power_theta)/2
power_alpha=(CH1power_alpha+CH2power_alpha)/2
power_beta=(CH1power_beta+CH2power_beta)/2

relaxaux=[]
for i in range(0,len(spec_t)):
	if((power_alpha[i]>power_theta[i]*np.sqrt(2)) & (power_alpha[i]>power_beta[i]*np.sqrt(2))):
		relaxaux.append(1)
	else:
		relaxaux.append(0)

relax=[]
if((relaxaux[0]==1) & (relaxaux[1]==1)):
	relax.append(1)
else:
	relax.append(0)
for i in range(1,len(relaxaux)-1):
	if((relaxaux[i-1]==1) & (relaxaux[i]==1) & (relaxaux[i+1]==1)):
		relax.append(1)
	else:
		relax.append(0)
if((relaxaux[len(relaxaux)-2]==1) & (relaxaux[len(relaxaux)-1]==1)):
	relax.append(1)
else:
	relax.append(0)

print("Comienza")

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 5204             # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
i=1
while conn:
	print('Connected by', addr)
	while i<len(relax):
		conn.send(str(relax[i]).encode())
		time.sleep(1/250)
		i=i+1
	break
conn.close()
print("Fin")


# plt.figure(1)
# plt.plot(spec_t,10*np.log10(power_alpha))
# plt.xlabel('Time (sec)')
# plt.ylabel('PSD per Hz (dB/Hz)')
# plt.title("PSD alpha waves over time")
# plt.show()

# plt.figure(2)
# plt.plot(spec_t,)
# plt.xlabel('Time (sec)')
# plt.ylabel('Relajación')
# plt.title("Estados de relajación en el tiempo")
# plt.show()

