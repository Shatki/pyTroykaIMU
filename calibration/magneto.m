instrreset;

% Enter Your Raspberry Pi pyIMUCalibrationDataServer host
HOST = '192.168.0.76';
PORT = 21566;

% Clear console and workspace
clc;
close all;

% Geting data from Serial
%s = serial('/dev/tty.serial1', 'BaudRate', 115200);

% Getting data from TCP/IP
s = tcpip(HOST, PORT);

fopen(s);
fileID = fopen('calibrate.txt', 'w');

for n = 1:3000
    str1= fscanf(s, '%c', 128);
    disp([int2str(n), char(9), str1]);
    C = strsplit(str1, ';');

    m_x=str2double(C(1));
    m_y=str2double(C(2));
    m_z=str2double(C(3));

    %a_x=str2double(C(4));
    %a_y=str2double(C(5));
    %a_z=str2double(C(6));

    %g_x=str2double(C(7));
    %g_y=str2double(C(8));
    %g_z=str2double(C(9));

    scatter3(m_x, m_y, m_z, 3);

    hold on;
    axis equal;
    fprintf(fileID, '%f %f %f \r\n', m_x, m_y, m_z);

    pause(0.05);
end

fclose(fileID);
fclose(s);
delete(s);
clear s;